# Lycon2

A maintained fork of [lycon](https://github.com/ethereon/lycon), a minimal and fast image library for Python and C++.

Tested on:

- anaconda3 on Linux (Ubuntu 18.04) with Python`3.6`.

## Install

```
pip install lycon2
```

## Example

```python
import lycon2

# Load an image as a numpy array
img = lycon2.imread('mittens.jpg')
# Resize the image using bicubic interpolation
resized = lycon2.resize(img, (256, 512), interpolation=lycon2.Interpolation.CUBIC)
# Crop the image (like any regular numpy array)
cropped = resized[:100, :200]
# Save the image
lycon2.imwrite('cropped-mittens.png', cropped)
```

## License

- Lycon2 is a modernized fork of Lycon maintained by the PettingZoo team.
- All code derived from the OpenCV project is licensed under the 3-clause BSD License.
- All Lycon-specific modifications are licensed under the MIT license.

See `LICENSE` for further details.
