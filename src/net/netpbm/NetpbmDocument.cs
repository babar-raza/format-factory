// FormatFactory.Netpbm -- Commercial .NET Netpbm Document Model
// GAP-PROD-INV-NETPBM-001: NetpbmDocument sealed class following CsvDocument/FodsDocument pattern.
// commercial_product_ready: false

using System;
using System.IO;

namespace FormatFactory.Netpbm;

/// <summary>
/// High-level Netpbm document model — a document-level wrapper over NetpbmImage,
/// following the CsvDocument/FodsDocument pattern used by other Format Factory products.
///
/// Provides Load, Save, and inspection APIs without requiring direct use of
/// NetpbmParser or NetpbmWriter.
/// </summary>
public sealed class NetpbmDocument
{
    /// <summary>Underlying parsed image model.</summary>
    public NetpbmImage Image { get; }

    /// <summary>Image width in pixels.</summary>
    public int Width => Image.Width;

    /// <summary>Image height in pixels.</summary>
    public int Height => Image.Height;

    /// <summary>Netpbm format variant (P1–P6).</summary>
    public NetpbmFormat Format => Image.Format;

    /// <summary>Total pixel count (Width * Height).</summary>
    public int PixelCount => Image.Width * Image.Height;

    /// <summary>Maximum pixel value. PBM=1, PGM/PPM typically 255.</summary>
    public int MaxValue => Image.MaxValue;

    /// <summary>True if this is a color image (PPM P3 or P6).</summary>
    public bool IsColor => Format is NetpbmFormat.PPM_P3 or NetpbmFormat.PPM_P6;

    /// <summary>True if this is a grayscale image (PGM P2 or P5).</summary>
    public bool IsGrayscale => Format is NetpbmFormat.PGM_P2 or NetpbmFormat.PGM_P5;

    /// <summary>True if this is a bitmap image (PBM P1 or P4).</summary>
    public bool IsBitmap => Format is NetpbmFormat.PBM_P1 or NetpbmFormat.PBM_P4;

    /// <summary>Aspect ratio as Width / Height. Returns 0 if Height is 0.</summary>
    public double AspectRatio => Height == 0 ? 0.0 : (double)Width / Height;

    /// <summary>True if Width equals Height.</summary>
    public bool IsSquare => Width == Height;

    /// <summary>Source file path, if loaded from disk (null if loaded from stream).</summary>
    public string? SourcePath { get; }

    private NetpbmDocument(NetpbmImage image, string? sourcePath)
    {
        Image = image;
        SourcePath = sourcePath;
    }

    /// <summary>
    /// Load a Netpbm document from a file path.
    /// Supports P1/P2/P3 (ASCII) and P4/P5/P6 (binary).
    /// </summary>
    public static NetpbmDocument Load(string path)
    {
        var image = NetpbmParser.Parse(path);
        return new NetpbmDocument(image, path);
    }

    /// <summary>
    /// Load a Netpbm document from a stream (e.g. for testing or in-memory use).
    /// </summary>
    public static NetpbmDocument LoadStream(Stream stream)
    {
        var image = NetpbmParser.ParseStream(stream);
        return new NetpbmDocument(image, null);
    }

    /// <summary>
    /// Wrap an existing NetpbmImage in a document.
    /// </summary>
    public static NetpbmDocument FromImage(NetpbmImage image)
    {
        if (image is null) throw new ArgumentNullException(nameof(image));
        return new NetpbmDocument(image, null);
    }

    /// <summary>
    /// Save the document to a file path.
    /// Binary formats (P4/P5/P6) are written as binary; ASCII (P1/P2/P3) as text.
    /// </summary>
    public void Save(string path) => NetpbmWriter.Write(Image, path);

    /// <summary>
    /// Get the pixel value at (row, col).
    /// For PBM/PGM: single byte. For PPM: red channel (use GetPixelColor for RGB).
    /// </summary>
    public byte GetPixel(int row, int col) => Image.GetPixel(row, col);

    /// <summary>Get the RGB pixel color at (row, col). For PBM/PGM, R=G=B=grayscale.</summary>
    public (byte R, byte G, byte B) GetPixelColor(int row, int col) => Image.GetPixelColor(row, col);

    /// <summary>Serialize to ASCII Netpbm string (P1/P2/P3).</summary>
    public string ToAsciiString() => NetpbmWriter.ToAsciiString(Image);

    /// <summary>Serialize to binary Netpbm bytes (P4/P5/P6).</summary>
    public byte[] ToBinaryBytes() => NetpbmWriter.ToBinaryBytes(Image);
}
