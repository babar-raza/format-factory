// FormatFactory.Netpbm -- NetpbmImage pixel filters and effects (partial class).
// Extracted from NetpbmImage.cs via TC-NET-H3 (LOC decomposition).

using System;
using System.Collections.Generic;

namespace FormatFactory.Netpbm;

public sealed partial class NetpbmImage
{
    /// <summary>
    /// Invert all pixel values in place.
    /// PBM: 0↔1. PGM: v → MaxValue - v. PPM: each channel inverted.
    /// R88 Train J: invert transform API.
    /// </summary>
    public void Invert()
    {
        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
        {
            byte max = (byte)MaxValue;
            int len = Width * Height;
            for (int i = 0; i < len; i++)
            {
                RedChannel![i] = (byte)(max - RedChannel[i]);
                GreenChannel![i] = (byte)(max - GreenChannel[i]);
                BlueChannel![i] = (byte)(max - BlueChannel[i]);
            }
        }
        else if (Format == NetpbmFormat.PBM_P1 || Format == NetpbmFormat.PBM_P4)
        {
            for (int i = 0; i < Pixels.Length; i++)
                Pixels[i] = (byte)(1 - Pixels[i]);
        }
        else
        {
            byte max = (byte)MaxValue;
            for (int i = 0; i < Pixels.Length; i++)
                Pixels[i] = (byte)(max - Pixels[i]);
        }
    }

    /// <summary>
    /// Adjust brightness by adding a delta to all pixel values, clamped to [0, MaxValue].
    /// Returns a NEW image.
    /// R104 Wave 1: pixel intensity adjustment for image processing pipeline.
    /// </summary>
    public NetpbmImage AdjustBrightness(int delta)
    {
        var result = Clone();
        if (Format == NetpbmFormat.PBM_P1 || Format == NetpbmFormat.PBM_P4)
            return result;

        int max = MaxValue;
        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
        {
            for (int i = 0; i < result.RedChannel!.Length; i++)
            {
                result.RedChannel[i] = (byte)Math.Clamp(result.RedChannel[i] + delta, 0, max);
                result.GreenChannel![i] = (byte)Math.Clamp(result.GreenChannel[i] + delta, 0, max);
                result.BlueChannel![i] = (byte)Math.Clamp(result.BlueChannel[i] + delta, 0, max);
            }
        }
        else
        {
            for (int i = 0; i < result.Pixels.Length; i++)
                result.Pixels[i] = (byte)Math.Clamp(result.Pixels[i] + delta, 0, max);
        }
        return result;
    }

    /// <summary>
    /// Adjust contrast by scaling pixel values around the midpoint (MaxValue/2).
    /// Returns a NEW image.
    /// R105 Wave 2: contrast adjustment for image processing pipeline.
    /// </summary>
    public NetpbmImage AdjustContrast(double factor)
    {
        if (factor < 0)
            throw new ArgumentOutOfRangeException(nameof(factor), "Contrast factor must not be negative.");

        var result = Clone();
        if (Format == NetpbmFormat.PBM_P1 || Format == NetpbmFormat.PBM_P4)
            return result;

        double mid = MaxValue / 2.0;
        int max = MaxValue;

        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
        {
            for (int i = 0; i < result.RedChannel!.Length; i++)
            {
                result.RedChannel[i] = (byte)Math.Clamp((int)Math.Round(mid + (result.RedChannel[i] - mid) * factor), 0, max);
                result.GreenChannel![i] = (byte)Math.Clamp((int)Math.Round(mid + (result.GreenChannel[i] - mid) * factor), 0, max);
                result.BlueChannel![i] = (byte)Math.Clamp((int)Math.Round(mid + (result.BlueChannel[i] - mid) * factor), 0, max);
            }
        }
        else
        {
            for (int i = 0; i < result.Pixels.Length; i++)
                result.Pixels[i] = (byte)Math.Clamp((int)Math.Round(mid + (result.Pixels[i] - mid) * factor), 0, max);
        }
        return result;
    }

    /// <summary>
    /// Perform histogram equalization on PGM images to improve contrast.
    /// R107 Wave 2: image enhancement for processing pipeline depth.
    /// </summary>
    public NetpbmImage Equalize()
    {
        if (Format == NetpbmFormat.PBM_P1 || Format == NetpbmFormat.PBM_P4)
            return Clone();

        NetpbmImage source = this;
        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
            source = ToGrayscale();

        int totalPixels = source.Width * source.Height;
        if (totalPixels == 0) return source.Clone();

        var hist = new int[source.MaxValue + 1];
        foreach (var p in source.Pixels)
            hist[Math.Clamp((int)p, 0, source.MaxValue)]++;

        var cdf = new int[hist.Length];
        cdf[0] = hist[0];
        for (int i = 1; i < hist.Length; i++)
            cdf[i] = cdf[i - 1] + hist[i];

        int cdfMin = 0;
        for (int i = 0; i < cdf.Length; i++)
        {
            if (cdf[i] > 0) { cdfMin = cdf[i]; break; }
        }

        var lut = new byte[hist.Length];
        int denom = totalPixels - cdfMin;
        if (denom <= 0) return source.Clone();
        for (int i = 0; i < lut.Length; i++)
        {
            lut[i] = (byte)Math.Clamp(
                (int)Math.Round((double)(cdf[i] - cdfMin) / denom * source.MaxValue),
                0, source.MaxValue);
        }

        var result = new NetpbmImage
        {
            Format = source.Format,
            Width = source.Width,
            Height = source.Height,
            MaxValue = source.MaxValue,
            Pixels = new byte[totalPixels],
        };

        for (int i = 0; i < totalPixels; i++)
            result.Pixels[i] = lut[Math.Clamp((int)source.Pixels[i], 0, source.MaxValue)];

        return result;
    }

    /// <summary>
    /// Convert an image to a 1-bit PBM bitmap by thresholding.
    /// R102 Train C: binarization for document scanning pipeline.
    /// </summary>
    public NetpbmImage Threshold(int threshold)
    {
        if (Format == NetpbmFormat.PBM_P1 || Format == NetpbmFormat.PBM_P4)
            throw new InvalidOperationException("Cannot threshold an already-binary PBM image.");

        if (threshold < 0 || threshold > MaxValue)
            throw new ArgumentOutOfRangeException(nameof(threshold),
                $"Threshold must be 0..{MaxValue}, got {threshold}.");

        int totalPixels = Width * Height;
        var result = new NetpbmImage
        {
            Format = NetpbmFormat.PBM_P1,
            Width = Width,
            Height = Height,
            MaxValue = 1,
            Pixels = new byte[totalPixels],
        };

        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
        {
            if (RedChannel == null || GreenChannel == null || BlueChannel == null)
                return result;
            for (int i = 0; i < totalPixels; i++)
            {
                int lum = (int)(0.299 * RedChannel[i] + 0.587 * GreenChannel[i] + 0.114 * BlueChannel[i]);
                result.Pixels[i] = lum >= threshold ? (byte)1 : (byte)0;
            }
        }
        else
        {
            for (int i = 0; i < totalPixels; i++)
                result.Pixels[i] = Pixels[i] >= threshold ? (byte)1 : (byte)0;
        }

        return result;
    }

    /// <summary>
    /// Apply gamma correction to the image.
    /// R108 Lane E: gamma correction for image processing pipeline.
    /// </summary>
    public NetpbmImage ApplyGamma(double gamma)
    {
        if (gamma <= 0)
            throw new ArgumentOutOfRangeException(nameof(gamma), "Gamma must be positive.");

        var result = Clone();
        if (IsPbm(Format)) return result;

        int max = MaxValue;
        if (IsPpm(Format))
        {
            for (int i = 0; i < result.RedChannel!.Length; i++)
            {
                result.RedChannel[i] = (byte)Math.Clamp(
                    (int)Math.Round(max * Math.Pow(result.RedChannel[i] / (double)max, gamma)), 0, max);
                result.GreenChannel![i] = (byte)Math.Clamp(
                    (int)Math.Round(max * Math.Pow(result.GreenChannel[i] / (double)max, gamma)), 0, max);
                result.BlueChannel![i] = (byte)Math.Clamp(
                    (int)Math.Round(max * Math.Pow(result.BlueChannel[i] / (double)max, gamma)), 0, max);
            }
        }
        else
        {
            for (int i = 0; i < result.Pixels.Length; i++)
                result.Pixels[i] = (byte)Math.Clamp(
                    (int)Math.Round(max * Math.Pow(result.Pixels[i] / (double)max, gamma)), 0, max);
        }
        return result;
    }

    /// <summary>
    /// Posterize the image by reducing pixel values to a fixed number of levels.
    /// R109 Lane E: posterization for artistic/reduced-palette image processing.
    /// </summary>
    public NetpbmImage Posterize(int levels)
    {
        if (levels < 2)
            throw new ArgumentOutOfRangeException(nameof(levels), "Levels must be at least 2.");

        var result = Clone();
        if (IsPbm(Format)) return result;

        int max = MaxValue;
        if (IsPpm(Format))
        {
            for (int i = 0; i < result.RedChannel!.Length; i++)
            {
                result.RedChannel[i] = Quantize(result.RedChannel[i], max, levels);
                result.GreenChannel![i] = Quantize(result.GreenChannel[i], max, levels);
                result.BlueChannel![i] = Quantize(result.BlueChannel[i], max, levels);
            }
        }
        else
        {
            for (int i = 0; i < result.Pixels.Length; i++)
                result.Pixels[i] = Quantize(result.Pixels[i], max, levels);
        }
        return result;
    }

    private static byte Quantize(byte value, int max, int levels)
    {
        double normalized = value / (double)max;
        int bucket = (int)Math.Floor(normalized * (levels - 1) + 0.5);
        bucket = Math.Clamp(bucket, 0, levels - 1);
        return (byte)Math.Clamp((int)Math.Round(bucket * max / (double)(levels - 1)), 0, max);
    }

    /// <summary>
    /// Create a solarized copy of this image. Pixels above the threshold are inverted.
    /// R110 Wave 4: artistic image processing depth.
    /// </summary>
    public NetpbmImage Solarize(byte threshold)
    {
        var result = Clone();
        if (IsPbm(Format)) return result;

        int max = MaxValue;
        if (IsPpm(Format))
        {
            for (int i = 0; i < result.RedChannel!.Length; i++)
            {
                if (result.RedChannel[i] > threshold)
                    result.RedChannel[i] = (byte)(max - result.RedChannel[i]);
                if (result.GreenChannel![i] > threshold)
                    result.GreenChannel[i] = (byte)(max - result.GreenChannel[i]);
                if (result.BlueChannel![i] > threshold)
                    result.BlueChannel[i] = (byte)(max - result.BlueChannel[i]);
            }
        }
        else
        {
            for (int i = 0; i < result.Pixels.Length; i++)
            {
                if (result.Pixels[i] > threshold)
                    result.Pixels[i] = (byte)(max - result.Pixels[i]);
            }
        }
        return result;
    }

    /// <summary>
    /// Create a sepia-toned copy of this image. Only applies to PPM images.
    /// R110 Wave 4: color tone processing for image manipulation.
    /// </summary>
    public NetpbmImage Sepia()
    {
        var result = Clone();
        if (!IsPpm(Format)) return result;

        int max = MaxValue;
        for (int i = 0; i < result.RedChannel!.Length; i++)
        {
            double lum = 0.299 * result.RedChannel[i] + 0.587 * result.GreenChannel![i] + 0.114 * result.BlueChannel![i];
            result.RedChannel[i] = (byte)Math.Clamp((int)Math.Round(lum * 1.0), 0, max);
            result.GreenChannel[i] = (byte)Math.Clamp((int)Math.Round(lum * 0.8), 0, max);
            result.BlueChannel[i] = (byte)Math.Clamp((int)Math.Round(lum * 0.6), 0, max);
        }
        return result;
    }

    /// <summary>
    /// Apply a 3x3 sharpening kernel to the image. Returns a new sharpened image.
    /// R111 Wave 5: image processing depth for enhancement workflows.
    /// </summary>
    public NetpbmImage Sharpen()
    {
        var result = Clone();
        if (IsPbm(Format)) return result;

        int w = Width, h = Height, max = MaxValue;
        if (IsPpm(Format))
        {
            var srcR = (byte[])RedChannel!.Clone();
            var srcG = (byte[])GreenChannel!.Clone();
            var srcB = (byte[])BlueChannel!.Clone();
            for (int y = 1; y < h - 1; y++)
            for (int x = 1; x < w - 1; x++)
            {
                int idx = y * w + x;
                int rVal = 5 * srcR[idx] - srcR[(y-1)*w+x] - srcR[(y+1)*w+x] - srcR[y*w+x-1] - srcR[y*w+x+1];
                int gVal = 5 * srcG[idx] - srcG[(y-1)*w+x] - srcG[(y+1)*w+x] - srcG[y*w+x-1] - srcG[y*w+x+1];
                int bVal = 5 * srcB[idx] - srcB[(y-1)*w+x] - srcB[(y+1)*w+x] - srcB[y*w+x-1] - srcB[y*w+x+1];
                result.RedChannel![idx] = (byte)Math.Clamp(rVal, 0, max);
                result.GreenChannel![idx] = (byte)Math.Clamp(gVal, 0, max);
                result.BlueChannel![idx] = (byte)Math.Clamp(bVal, 0, max);
            }
        }
        else
        {
            var src = (byte[])Pixels.Clone();
            for (int y = 1; y < h - 1; y++)
            for (int x = 1; x < w - 1; x++)
            {
                int idx = y * w + x;
                int val = 5 * src[idx] - src[(y-1)*w+x] - src[(y+1)*w+x] - src[y*w+x-1] - src[y*w+x+1];
                result.Pixels[idx] = (byte)Math.Clamp(val, 0, max);
            }
        }
        return result;
    }

    /// <summary>
    /// Apply an NxN box blur to the image. Returns a new blurred image.
    /// R111 Wave 5: image processing depth for smoothing workflows.
    /// </summary>
    public NetpbmImage BlurBox(int radius)
    {
        if (radius < 1)
            throw new ArgumentOutOfRangeException(nameof(radius), "Radius must be at least 1.");

        var result = Clone();
        if (IsPbm(Format)) return result;

        int w = Width, h = Height, max = MaxValue;

        if (IsPpm(Format))
        {
            for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
            {
                int sumR = 0, sumG = 0, sumB = 0, count = 0;
                for (int dy = -radius; dy <= radius; dy++)
                for (int dx = -radius; dx <= radius; dx++)
                {
                    int ny = y + dy, nx = x + dx;
                    if (ny >= 0 && ny < h && nx >= 0 && nx < w)
                    {
                        int ni = ny * w + nx;
                        sumR += RedChannel![ni];
                        sumG += GreenChannel![ni];
                        sumB += BlueChannel![ni];
                        count++;
                    }
                }
                int idx = y * w + x;
                result.RedChannel![idx] = (byte)Math.Clamp(sumR / count, 0, max);
                result.GreenChannel![idx] = (byte)Math.Clamp(sumG / count, 0, max);
                result.BlueChannel![idx] = (byte)Math.Clamp(sumB / count, 0, max);
            }
        }
        else
        {
            for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
            {
                int sum = 0, count = 0;
                for (int dy = -radius; dy <= radius; dy++)
                for (int dx = -radius; dx <= radius; dx++)
                {
                    int ny = y + dy, nx = x + dx;
                    if (ny >= 0 && ny < h && nx >= 0 && nx < w)
                    {
                        sum += Pixels[ny * w + nx];
                        count++;
                    }
                }
                result.Pixels[y * w + x] = (byte)Math.Clamp(sum / count, 0, max);
            }
        }
        return result;
    }

    /// <summary>
    /// Apply a box-based median filter with the given radius.
    /// R114 Train C: noise-reduction median filter for image processing pipelines.
    /// </summary>
    public NetpbmImage MedianFilter(int radius)
    {
        if (radius < 0)
            throw new ArgumentOutOfRangeException(nameof(radius), "Radius must be >= 0.");
        if (radius == 0) return Clone();

        bool color = IsPpm(Format);
        var result = Clone();

        if (color)
        {
            result.RedChannel = FilterChannel(RedChannel ?? Array.Empty<byte>(), Width, Height, radius);
            result.GreenChannel = FilterChannel(GreenChannel ?? Array.Empty<byte>(), Width, Height, radius);
            result.BlueChannel = FilterChannel(BlueChannel ?? Array.Empty<byte>(), Width, Height, radius);
            var px = new byte[Width * Height * 3];
            var r = result.RedChannel;
            var g = result.GreenChannel;
            var b = result.BlueChannel;
            for (int i = 0; i < Width * Height; i++)
            {
                px[i * 3] = r[i];
                px[i * 3 + 1] = g[i];
                px[i * 3 + 2] = b[i];
            }
            result.Pixels = px;
        }
        else
        {
            result.Pixels = FilterChannel(Pixels, Width, Height, radius);
        }

        return result;
    }

    private static byte[] FilterChannel(byte[] src, int w, int h, int radius)
    {
        var dst = new byte[src.Length];
        var window = new List<byte>((2 * radius + 1) * (2 * radius + 1));
        for (int row = 0; row < h; row++)
        {
            for (int col = 0; col < w; col++)
            {
                window.Clear();
                for (int dr = -radius; dr <= radius; dr++)
                {
                    int nr = Math.Clamp(row + dr, 0, h - 1);
                    for (int dc = -radius; dc <= radius; dc++)
                    {
                        int nc = Math.Clamp(col + dc, 0, w - 1);
                        window.Add(src[nr * w + nc]);
                    }
                }
                window.Sort();
                dst[row * w + col] = window[window.Count / 2];
            }
        }
        return dst;
    }
}
