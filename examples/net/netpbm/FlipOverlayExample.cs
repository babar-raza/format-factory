// Example: Netpbm FlipDiagonal + Overlay
// Demonstrates transposing an image and compositing a patch onto it.

using FormatFactory.Netpbm;

// Create a 4x2 grayscale gradient
var img = new NetpbmImage
{
    Format = NetpbmFormat.PGM_P2,
    Width = 4, Height = 2, MaxValue = 255,
    Pixels = new byte[] { 0, 50, 100, 150, 200, 250, 200, 100 }
};

Console.WriteLine($"Original: {img.Width}x{img.Height}");

// Transpose (flip along main diagonal)
var transposed = img.FlipDiagonal();
Console.WriteLine($"Transposed: {transposed.Width}x{transposed.Height}");

// Create a bright patch
var patch = new NetpbmImage
{
    Format = NetpbmFormat.PGM_P2,
    Width = 1, Height = 1, MaxValue = 255,
    Pixels = new byte[] { 255 }
};

// Overlay the patch at position (1,0)
var result = transposed.Overlay(patch, 1, 0);
Console.WriteLine($"After overlay: pixel at (1,0) = {result.Pixels[1 * result.Width + 0]}");
