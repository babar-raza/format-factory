// FormatFactory.Netpbm -- Commercial .NET Netpbm Cross-Format Exporter
// DEC-033 Option B: .NET Commercial Only
// Gate 11 status: NOT_STARTED (R85 first slice)
// commercial_product_ready: false
//
// Dogfooding strategy:
//   PBM → PGM: Expand 1-bit bitmap to 8-bit grayscale using Format Factory Netpbm model
//   (Uses Format Factory's own NetpbmImage model — no external library)

using System;

namespace FormatFactory.Netpbm;

/// <summary>
/// Cross-format export within the Netpbm family.
///
/// Dogfooding: all exports use Format Factory's own NetpbmImage model.
/// No external image libraries.
///
/// dogfood_status: IMPLEMENTED (PBM→PGM, PBM→PPM grayscale)
/// target_ff_library: FormatFactory.Netpbm.NetpbmWriter
/// </summary>
public static class NetpbmExporter
{
    /// <summary>
    /// Convert a PBM (1-bit bitmap) image to PGM (8-bit grayscale).
    ///
    /// Dogfood path: uses Format Factory NetpbmImage model.
    /// Mapping: PBM 0 (white) → PGM 255 (white), PBM 1 (black) → PGM 0 (black)
    /// </summary>
    public static NetpbmImage PbmToPgm(NetpbmImage pbm, int maxValue = 255)
    {
        if (pbm.Format is not (NetpbmFormat.PBM_P1 or NetpbmFormat.PBM_P4))
            throw new ArgumentException("Input must be PBM format.", nameof(pbm));
        if (pbm.Pixels == null || pbm.Pixels.Length == 0)
            throw new NetpbmException("PBM image has no pixel data.");

        var pgm = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = pbm.Width,
            Height = pbm.Height,
            MaxValue = maxValue,
            Pixels = new byte[pbm.Pixels.Length]
        };

        // PBM: 1=black (0 in PGM), 0=white (maxValue in PGM)
        for (int i = 0; i < pbm.Pixels.Length; i++)
            pgm.Pixels[i] = pbm.Pixels[i] == 1 ? (byte)0 : (byte)maxValue;

        foreach (var comment in pbm.Comments)
            pgm.Comments.Add(comment);
        pgm.Comments.Add("Converted from PBM by FormatFactory.Netpbm — dogfood export");

        return pgm;
    }

    /// <summary>
    /// Convert a PBM (1-bit bitmap) to a grayscale PPM image.
    ///
    /// Dogfood path: uses Format Factory NetpbmImage model.
    /// Mapping: PBM 0 (white) → PPM (255,255,255), PBM 1 (black) → PPM (0,0,0)
    /// </summary>
    public static NetpbmImage PbmToPpm(NetpbmImage pbm, int maxValue = 255)
    {
        if (pbm.Format is not (NetpbmFormat.PBM_P1 or NetpbmFormat.PBM_P4))
            throw new ArgumentException("Input must be PBM format.", nameof(pbm));

        long count = (long)pbm.Width * pbm.Height;
        var ppm = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3,
            Width = pbm.Width,
            Height = pbm.Height,
            MaxValue = maxValue,
            RedChannel = new byte[count],
            GreenChannel = new byte[count],
            BlueChannel = new byte[count]
        };

        for (long i = 0; i < count; i++)
        {
            byte v = pbm.Pixels[i] == 1 ? (byte)0 : (byte)maxValue;
            ppm.RedChannel[i] = v;
            ppm.GreenChannel[i] = v;
            ppm.BlueChannel[i] = v;
        }

        foreach (var comment in pbm.Comments)
            ppm.Comments.Add(comment);
        ppm.Comments.Add("Converted from PBM by FormatFactory.Netpbm — dogfood export");

        return ppm;
    }
}
