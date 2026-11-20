# Third-party components

## Bundled browser assets

WaveSurfer.js **8.1.0**, including the Regions plugin, is redistributed unchanged
from the npm package `wavesurfer.js@8.1.0` under BSD-3-Clause.

- Project: https://github.com/katspaugh/wavesurfer.js
- Full license: `assets/vendor/WAVESURFER-LICENSE`
- Package: https://registry.npmjs.org/wavesurfer.js/-/wavesurfer.js-8.1.0.tgz
- No runtime CDN requests or npm installation are required for the recorder.

- `wavesurfer.min.js` SHA-256: `9ede2d605b9b92ab3c4d9062ac53d56890e72809ea38f0394573a6672c7419f7`
- `regions.min.js` SHA-256: `539d34aeecf680f30b3e5f1571e5acfc41644d7c5ab563d37bbafc0f8656662b`

To update, obtain the chosen npm release, replace both minified bundles and its
license together, update these version/hash records, and run the Chrome integration
test including region selection/playback and interrupted recording recovery.

## Python processing dependency

ffmpeg-normalize **1.45.2** is installed by `requirements.txt`, not copied into
this repository. Its MIT-style license is published at
https://github.com/slhck/ffmpeg-normalize/blob/master/LICENSE.md.
Its transitive dependencies retain their own distributions and licenses.
