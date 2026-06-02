// FormatFactory.Netpbm — Load, Edit, Save Example
//
// Demonstrates: Parse a PGM image, edit pixels, apply transforms, save.
// This is a standalone example — not compiled as part of the test project.

using FormatFactory.Netpbm;

// 1. Parse a Netpbm file (P1-P6 all supported)
var image = NetpbmParser.Parse("input.pgm");
Console.WriteLine($"Format: {image.Format}, Size: {image.Width}x{image.Height}");

// 2. Read and write pixels
byte original = image.GetPixel(0, 0);
image.SetPixel(0, 0, 128);

// 3. Get statistics
var (mean, min, max) = image.GetStats();
Console.WriteLine($"Stats: mean={mean:F1}, min={min}, max={max}");

// 4. Apply transforms
image.FlipHorizontal();
image.FlipVertical();
image.Invert();

// 5. Rotate (returns new image — dimensions swap)
var rotated = image.Rotate90Cw();
Console.WriteLine($"Rotated: {rotated.Width}x{rotated.Height}");

// 6. Crop a region
var cropped = image.Crop(top: 10, left: 10, cropHeight: 50, cropWidth: 50);

// 7. Save
NetpbmWriter.Write(image, "output.pgm");

// 8. Cross-format export (dogfood: uses FF's own model)
var ppm = NetpbmExporter.PgmToPpm(image);
NetpbmWriter.Write(ppm, "output.ppm");
