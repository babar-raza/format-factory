// FormatFactory.Netpbm -- NetpbmImage analysis methods (partial class).
// Extracted from NetpbmImage.cs via TC-NET-H3 (LOC decomposition).

using System;

namespace FormatFactory.Netpbm;

public sealed partial class NetpbmImage
{
    /// <summary>Compute simple pixel statistics for PBM/PGM.</summary>
    public (double Mean, int Min, int Max) GetStats()
    {
        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
            throw new InvalidOperationException("Use GetChannelStats for PPM.");
        if (Pixels.Length == 0)
            return (0, 0, 0);
        long sum = 0;
        int min = Pixels[0], max = Pixels[0];
        foreach (var p in Pixels)
        {
            sum += p;
            if (p < min) min = p;
            if (p > max) max = p;
        }
        return ((double)sum / Pixels.Length, min, max);
    }

    /// <summary>
    /// Compute per-channel pixel statistics for PPM.
    /// Returns (R, G, B) where each is (Mean, Min, Max).
    /// R89 Train H: PPM statistics API.
    /// </summary>
    public ((double Mean, int Min, int Max) R, (double Mean, int Min, int Max) G, (double Mean, int Min, int Max) B) GetChannelStats()
    {
        if (Format != NetpbmFormat.PPM_P3 && Format != NetpbmFormat.PPM_P6)
            throw new InvalidOperationException("Use GetStats for PBM/PGM.");
        int len = Width * Height;
        if (len == 0)
            return ((0, 0, 0), (0, 0, 0), (0, 0, 0));

        static (double Mean, int Min, int Max) ComputeStats(byte[] ch, int count)
        {
            long sum = 0;
            int min = ch[0], max = ch[0];
            for (int i = 0; i < count; i++)
            {
                sum += ch[i];
                if (ch[i] < min) min = ch[i];
                if (ch[i] > max) max = ch[i];
            }
            return ((double)sum / count, min, max);
        }

        return (
            ComputeStats(RedChannel!, len),
            ComputeStats(GreenChannel!, len),
            ComputeStats(BlueChannel!, len)
        );
    }

    /// <summary>
    /// Compute the average brightness of the image as a value in [0.0, 1.0].
    /// R96 Train N: image brightness metric for analysis pipeline.
    /// </summary>
    public double GetBrightness()
    {
        int totalPixels = Width * Height;
        if (totalPixels == 0 || MaxValue == 0) return 0.0;

        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
        {
            if (RedChannel == null || GreenChannel == null || BlueChannel == null)
                return 0.0;
            double sum = 0;
            for (int i = 0; i < totalPixels; i++)
            {
                sum += 0.299 * RedChannel[i] + 0.587 * GreenChannel[i] + 0.114 * BlueChannel[i];
            }
            return sum / totalPixels / MaxValue;
        }
        else
        {
            long sum = 0;
            foreach (var p in Pixels)
                sum += p;
            return (double)sum / totalPixels / MaxValue;
        }
    }

    /// <summary>
    /// Compute a histogram of pixel intensities.
    /// R101 Train C: pixel distribution analysis for image quality pipeline.
    /// </summary>
    public int[] GetHistogram()
    {
        int totalPixels = Width * Height;
        if (totalPixels == 0)
            return Array.Empty<int>();

        if (Format == NetpbmFormat.PBM_P1 || Format == NetpbmFormat.PBM_P4)
        {
            var hist = new int[2];
            foreach (var p in Pixels)
                hist[Math.Clamp((int)p, 0, 1)]++;
            return hist;
        }

        int bins = MaxValue + 1;
        var histogram = new int[bins];

        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
        {
            if (RedChannel == null || GreenChannel == null || BlueChannel == null)
                return histogram;
            for (int i = 0; i < totalPixels; i++)
            {
                int lum = (int)(0.299 * RedChannel[i] + 0.587 * GreenChannel[i] + 0.114 * BlueChannel[i]);
                histogram[Math.Clamp(lum, 0, MaxValue)]++;
            }
        }
        else
        {
            foreach (var p in Pixels)
                histogram[Math.Clamp((int)p, 0, MaxValue)]++;
        }

        return histogram;
    }

    /// <summary>
    /// Return a flattened array of per-pixel brightness values (0.0–1.0).
    /// R115 Train B: brightness map for image analysis pipeline.
    /// </summary>
    public double[] GetBrightnessMap()
    {
        int n = Width * Height;
        var map = new double[n];
        double maxVal = MaxValue > 0 ? MaxValue : 255.0;

        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
        {
            var r = RedChannel ?? Array.Empty<byte>();
            var g = GreenChannel ?? Array.Empty<byte>();
            var b = BlueChannel ?? Array.Empty<byte>();
            for (int i = 0; i < n; i++)
                map[i] = (0.299 * (i < r.Length ? r[i] : 0)
                        + 0.587 * (i < g.Length ? g[i] : 0)
                        + 0.114 * (i < b.Length ? b[i] : 0)) / maxVal;
        }
        else
        {
            for (int i = 0; i < n && i < Pixels.Length; i++)
                map[i] = Pixels[i] / maxVal;
        }
        return map;
    }
}
