      basis: 'The source images establish the raised arrival condition and major masses. The exact path, retaining edges, stairs, and close-range details remain interpretive.',
      evidence: 'Interpretive',
      evidenceClass: 'evidence-interpretive',
      poster: 'left_center',
      video: 'left_center',
      aria: 'The field reveal from the left-center terrace',
      mapTitle: 'Left-center terrace',
      mapCopy: 'Move from public space into the first full field reveal.'
    },
    boat: {
      index: '03',
      location: 'Chicago River · Boat level',
      title: 'The river becomes the front door.',
      description: 'Travel along the waterline beneath the raised quay, restaurant, scoreboards, and outfield edge.',
      basis: 'The river, stadium edge, and principal buildings are source-backed. Low-level facade detail, activity, and the continuous boat route are reconstructed between fixed views.',
      evidence: 'Reconstructed',
      evidenceClass: 'evidence-reconstructed',
      poster: 'boat',
      video: 'boat',
      aria: 'The ballpark viewed from a boat on the Chicago River',
      mapTitle: 'River edge',
      mapCopy: 'See the district from the water instead of the grandstand.'
    },
    river: {
      index: '04',
      location: 'Home plate to river · Modeled line',
      title: 'One imagined swing into the river.',
      description: 'Trace an authored home-run path from home plate, over the outfield structures, and beyond the modeled waterline.',
      basis: 'The current model measures 423 feet to the water and 469 feet to the illustrated splash along this chosen line. The arc is enlarged and authored for visibility; it is not an aerodynamic prediction or official dimension.',
      evidence: 'Illustrative',
      evidenceClass: 'evidence-illustrative',
      poster: 'river-poster',
      video: 'river',
      aria: 'An illustrated home run traveling from home plate to the Chicago River',
      mapTitle: 'River home run',
      mapCopy: 'Follow one measured, illustrative line from home plate to the water.'
    }
  };
  const sceneKeys = Object.keys(scenes);
  const tour = document.querySelector('[data-tour-shell]');
  const video = document.querySelector('#scene-video');
  const videoSource = video?.querySelector('source');
