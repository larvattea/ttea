KarTEA custom resources
=======================

Put images and sounds here to make them available on the player
configuration screen, alongside the ones that come with the game. Each
file goes in the folder of the resource it replaces:

  images/vehicle/              vehicle
  images/environment/          scenery (left and right)
  images/target/               target
  images/obstacle/             obstacle
  images/feedback/positive/    positive visual feedback
  images/feedback/neutral/     neutral visual feedback
  images/feedback/negative/    negative visual feedback
  sounds/feedback/positive/    hit sound
  sounds/feedback/neutral/     neutral sound
  sounds/feedback/negative/    miss sound

Accepted formats:
  images: .png (recommended, with a transparent background), .jpg,
          .jpeg, .bmp
  sounds: .wav

Recommendations
---------------

  Vehicle      512x512 pixels (at least 384x384 on Full HD screens).
               Square image, car seen from behind, transparent
               background. On screen, the car fills a square 1/5 of the
               screen width: a smaller image looks blurry, and a
               rectangular image ends up squashed.
  Target and   256x256 pixels (at least 100x100). Square image,
  obstacle     transparent background. The game shrinks the image to
               100x100 before the track perspective is applied: larger
               files do not improve quality.
  Scenery      size close to 500x520 pixels (like the original trees).
               The size on screen follows the file size: a very large
               image becomes a giant object, and a very small one a
               tiny object. The left and right images must face the
               correct side.
  Visual       size close to 800x200 pixels. It is shown at its
  feedback     original size, without resizing: a large photo covers
               the screen.
  Sounds       16-bit PCM .wav, short and about as loud as the
               original sounds. Compressed (ADPCM) or 32-bit WAV files
               may not play.

The neutral feedback (image and sound) can be selected, but it is not
used during the game.

After copying a file, close and reopen the configuration screen for it
to appear in the list. If a selected file is deleted, the game goes
back to the default resource.
