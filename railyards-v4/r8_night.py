"""Illustrative night glazing for landmark meshes; no geographic changes.

World-space bays avoid one random value per batched skyline mesh. Dimensions
and occupied-window patterns are inferred, not a survey of building interiors.
"""
import bpy


def apply_landmark_windows(scene, enabled):
    for obj in scene.objects:
        if obj.type != 'MESH' or not obj.name.startswith('D2_Skyline'):
            continue
        for slot in obj.material_slots:
            original = slot.material
            if original is None:
                continue
            base_name = original.get('night_base', original.name)
            if not base_name.startswith('D2_glass'):
                continue
            if not enabled:
                slot.material = bpy.data.materials.get(base_name, original)
                continue
            material_name = 'R8_windows_' + base_name
            material = bpy.data.materials.get(material_name)
            if material is None:
                material = bpy.data.materials[base_name].copy()
                material.name = material_name
                material['night_base'] = base_name
                nodes, links = material.node_tree.nodes, material.node_tree.links
                shader = nodes.get('Principled BSDF')
                geometry = nodes.new('ShaderNodeNewGeometry')
                scale = nodes.new('ShaderNodeVectorMath'); scale.operation = 'MULTIPLY'
                scale.inputs[1].default_value = (1 / 3.0, 1 / 3.0, 1 / 3.8)
                links.new(geometry.outputs['Position'], scale.inputs[0])
                split = nodes.new('ShaderNodeSeparateXYZ')
                links.new(scale.outputs['Vector'], split.inputs[0])

                def math_node(operation, a, b=None):
                    node = nodes.new('ShaderNodeMath'); node.operation = operation
                    if isinstance(a, (float, int)): node.inputs[0].default_value = a
                    else: links.new(a, node.inputs[0])
                    if b is not None:
                        if isinstance(b, (float, int)): node.inputs[1].default_value = b
                        else: links.new(b, node.inputs[1])
                    return node.outputs[0]

                normal = nodes.new('ShaderNodeSeparateXYZ')
                links.new(geometry.outputs['Normal'], normal.inputs[0])
                # Select the horizontal coordinate along each vertical facade.
                use_y = math_node('GREATER_THAN', math_node('ABSOLUTE', normal.outputs['X']), .5)
                x = math_node('MULTIPLY', split.outputs['X'], math_node('SUBTRACT', 1, use_y))
                y = math_node('MULTIPLY', split.outputs['Y'], use_y)
                along = math_node('ADD', x, y)
                horizontal = math_node('FRACT', along)
                vertical = math_node('FRACT', split.outputs['Z'])
                bay = math_node('MULTIPLY', math_node('GREATER_THAN', horizontal, .12), math_node('LESS_THAN', horizontal, .88))
                floor = math_node('MULTIPLY', math_node('GREATER_THAN', vertical, .20), math_node('LESS_THAN', vertical, .88))
                upright = math_node('LESS_THAN', math_node('ABSOLUTE', normal.outputs['Z']), .35)
                mask = math_node('MULTIPLY', math_node('MULTIPLY', bay, floor), upright)
                cells = nodes.new('ShaderNodeVectorMath'); cells.operation = 'FLOOR'
                links.new(scale.outputs['Vector'], cells.inputs[0])
                random = nodes.new('ShaderNodeTexWhiteNoise'); random.noise_dimensions = '3D'
                links.new(cells.outputs['Vector'], random.inputs['Vector'])
                occupied = math_node('GREATER_THAN', random.outputs['Value'], .80)
                emission = math_node('MULTIPLY', math_node('MULTIPLY', mask, occupied), .55)
                links.new(emission, shader.inputs['Emission Strength'])
                shader.inputs['Emission Color'].default_value = (1, .67, .34, 1)
                colors = nodes.new('ShaderNodeMixRGB')
                colors.inputs[1].default_value = (.012, .022, .035, 1)
                colors.inputs[2].default_value = tuple(shader.inputs['Base Color'].default_value)
                links.new(mask, colors.inputs[0]); links.new(colors.outputs[0], shader.inputs['Base Color'])
            slot.material = material
