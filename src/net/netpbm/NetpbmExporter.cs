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

    /// <summary>
    /// Convert a PGM (grayscale) image to PPM (color) by replicating the gray value
    /// into R, G, B channels.
    ///
    /// Dogfood path: uses Format Factory NetpbmImage model exclusively.
    /// R87 Train J / Train N: PGM → PPM dogfood export.
    /// </summary>
    public static NetpbmImage PgmToPpm(NetpbmImage pgm, int maxValue = 0)
    {
        if (pgm.Format is not (NetpbmFormat.PGM_P2 or NetpbmFormat.PGM_P5))
            throw new ArgumentException("Input must be PGM format.", nameof(pgm));
        if (pgm.Pixels == null || pgm.Pixels.Length == 0)
            throw new NetpbmException("PGM image has no pixel data.");

        int mv = maxValue > 0 ? maxValue : pgm.MaxValue;
        long count = (long)pgm.Width * pgm.Height;

        var ppm = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3,
            Width = pgm.Width,
            Height = pgm.Height,
            MaxValue = mv,
            RedChannel = new byte[count],
            GreenChannel = new byte[count],
            BlueChannel = new byte[count]
        };

        for (long i = 0; i < count && i < pgm.Pixels.Length; i++)
        {
            byte v = pgm.Pixels[i];
            ppm.RedChannel[i] = v;
            ppm.GreenChannel[i] = v;
            ppm.BlueChannel[i] = v;
        }

        foreach (var comment in pgm.Comments)
            ppm.Comments.Add(comment);
        ppm.Comments.Add("Converted from PGM by FormatFactory.Netpbm — dogfood export");

        return ppm;
    }

    /// <summary>
    /// Convert a PPM (color) image to PGM (grayscale) using luminance formula:
    /// gray = 0.299*R + 0.587*G + 0.114*B (standard BT.601 weights, integer approximation).
    ///
    /// Dogfood path: uses Format Factory NetpbmImage model exclusively.
    /// R87 Train J: PPM → PGM grayscale export.
    /// </summary>
    public static NetpbmImage PpmToPgm(NetpbmImage ppm, int maxValue = 0)
    {
        if (ppm.Format is not (NetpbmFormat.PPM_P3 or NetpbmFormat.PPM_P6))
            throw new ArgumentException("Input must be PPM format.", nameof(ppm));
        if (ppm.RedChannel == null || ppm.GreenChannel == null || ppm.BlueChannel == null)
            throw new NetpbmException("PPM image is missing color channels.");

        int mv = maxValue > 0 ? maxValue : ppm.MaxValue;
        long count = (long)ppm.Width * ppm.Height;

        var pgm = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = ppm.Width,
            Height = ppm.Height,
            MaxValue = mv,
            Pixels = new byte[count]
        };

        for (long i = 0; i < count; i++)
        {
            // BT.601 luminance: Y = 0.299R + 0.587G + 0.114B
            int gray = (299 * ppm.RedChannel[i] + 587 * ppm.GreenChannel[i] + 114 * ppm.BlueChannel[i]) / 1000;
            pgm.Pixels[i] = (byte)Math.Min(gray, mv);
        }

        foreach (var comment in ppm.Comments)
            pgm.Comments.Add(comment);
        pgm.Comments.Add("Converted from PPM by FormatFactory.Netpbm — dogfood grayscale export");

        return pgm;
    }
}
