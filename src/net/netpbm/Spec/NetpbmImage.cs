// FormatFactory.Netpbm — Spec.NetpbmImage — Canonical spec-shaped model class
// spec_qname: netpbm:image
// TC-QHARD-052: new canonical spec authority class for Netpbm format family
namespace FormatFactory.Netpbm.Spec;

/// <summary>
/// Canonical spec-shaped model class for a Netpbm image (PBM, PGM, or PPM).
///
/// The Netpbm format family (PBM=bitmap, PGM=graymap, PPM=pixmap) stores
/// raster images as plain or raw binary data with a P1–P6 magic number header.
/// spec_qname: netpbm:image
///
/// This is a canonical class in the Spec/ hierarchy. The behavioral model is
/// FormatFactory.Netpbm.Model.NetpbmImage (in Model/).
/// </summary>
public sealed class NetpbmImage
{
    /// <summary>The spec QName for a Netpbm image element.</summary>
    public const string SpecQName = "netpbm:image";

    /// <summary>
    /// The Netpbm magic number identifying the format variant.
    /// P1/P4=PBM (bitmap), P2/P5=PGM (graymap), P3/P6=PPM (pixmap).
    /// </summary>
    public string MagicNumber { get; init; } = string.Empty;

    /// <summary>Image width in pixels.</summary>
    public int Width { get; init; }

    /// <summary>Image height in pixels.</summary>
    public int Height { get; init; }

    /// <summary>Maximum sample value (1 for PBM, 1–65535 for PGM/PPM).</summary>
    public int MaxVal { get; init; }
}
