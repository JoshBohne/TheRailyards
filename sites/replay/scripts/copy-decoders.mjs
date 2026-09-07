import {cp,mkdir} from 'node:fs/promises';
await mkdir('public/draco',{recursive:true});
await cp('node_modules/three/examples/jsm/libs/draco/gltf','public/draco',{recursive:true});
