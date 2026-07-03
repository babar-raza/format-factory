// FormatFactory.Netpbm -- NetpbmImage geometric transforms and composition (partial class).
// Extracted from NetpbmImage.cs via TC-NET-H3 (LOC decomposition).

using System;
using System.Collections.Generic;

namespace FormatFactory.Netpbm;

public sealed partial class NetpbmImage
{
    /// <summary>
    /// Flip the image horizontally (mirror left-right) in place.
    /// simple transform API.
    /// </summary>
    public void FlipHorizontal()
    {
        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
        {
            for (int row = 0; row < Height; row++)
            {
                for (int left = 0, right = Width - 1; left < right; left++, right--)
                {
                    int li = row * Width + left;
                    int ri = row * Width + right;
                    (RedChannel![li], RedChannel[ri]) = (RedChannel[ri], RedChannel[li]);
                    (GreenChannel![li], GreenChannel[ri]) = (GreenChannel[ri], GreenChannel[li]);
                    (BlueChannel![li], BlueChannel[ri]) = (BlueChannel[ri], BlueChannel[li]);
                }
            }
        }
        else
        {
            for (int row = 0; row < Height; row++)
            {
                for (int left = 0, right = Width - 1; left < right; left++, right--)
                {
                    int li = row * Width + left;
                    int ri = row * Width + right;
                    (Pixels[li], Pixels[ri]) = (Pixels[ri], Pixels[li]);
                }
            }
        }
    }

    /// <summary>
    /// Flip the image vertically (mirror top-bottom) in place.
    /// vertical transform API.
    /// </summary>
    public void FlipVertical()
    {
        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
        {
            for (int top = 0, bot = Height - 1; top < bot; top++, bot--)
            {
                for (int col = 0; col < Width; col++)
                {
                    int ti = top * Width + col;
                    int bi = bot * Width + col;
                    (RedChannel![ti], RedChannel[bi]) = (RedChannel[bi], RedChannel[ti]);
                    (GreenChannel![ti], GreenChannel[bi]) = (GreenChannel[bi], GreenChannel[ti]);
                    (BlueChannel![ti], BlueChannel[bi]) = (BlueChannel[bi], BlueChannel[ti]);
                }
            }
        }
        else
        {
            for (int top = 0, bot = Height - 1; top < bot; top++, bot--)
            {
                for (int col = 0; col < Width; col++)
                {
                    int ti = top * Width + col;
                    int bi = bot * Width + col;
                    (Pixels[ti], Pixels[bi]) = (Pixels[bi], Pixels[ti]);
                }
            }
        }
    }

    /// <summary>
    /// Rotate the image 90° clockwise. Returns a NEW image (dimensions swap).
    /// rotation transform.
    /// </summary>
    public NetpbmImage Rotate90Cw()
    {
        var result = new NetpbmImage
        {
            Format = Format,
            Width = Height,
            Height = Width,
            MaxValue = MaxValue,
            SourcePath = SourcePath
        };
        result.Comments.AddRange(Comments);

        int newW = result.Width;
        int newH = result.Height;

        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
        {
            int len = newW * newH;
            result.RedChannel = new byte[len];
            result.GreenChannel = new byte[len];
            result.BlueChannel = new byte[len];
            result.Pixels = Array.Empty<byte>();

            for (int r = 0; r < Height; r++)
            {
                for (int c = 0; c < Width; c++)
                {
                    int srcIdx = r * Width + c;
                    int dstRow = c;
                    int dstCol = Height - 1 - r;
                    int dstIdx = dstRow * newW + dstCol;
                    result.RedChannel[dstIdx] = RedChannel![srcIdx];
                    result.GreenChannel[dstIdx] = GreenChannel![srcIdx];
                    result.BlueChannel[dstIdx] = BlueChannel![srcIdx];
                }
            }
        }
        else
        {
            result.Pixels = new byte[newW * newH];
            for (int r = 0; r < Height; r++)
            {
                for (int c = 0; c < Width; c++)
                {
                    int dstRow = c;
                    int dstCol = Height - 1 - r;
                    result.Pixels[dstRow * newW + dstCol] = Pixels[r * Width + c];
                }
            }
        }

        return result;
    }

    /// <summary>
    /// Rotate the image 270° clockwise (90° counter-clockwise). Returns a NEW image (dimensions swap).
    /// counter-clockwise rotation.
    /// </summary>
    public NetpbmImage Rotate270Cw()
    {
        var result = new NetpbmImage
        {
            Format = Format,
            Width = Height,
            Height = Width,
            MaxValue = MaxValue,
            SourcePath = SourcePath
        };
        result.Comments.AddRange(Comments);

        int newW = result.Width;
        int newH = result.Height;

        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
        {
            int len = newW * newH;
            result.RedChannel = new byte[len];
            result.GreenChannel = new byte[len];
            result.BlueChannel = new byte[len];
            result.Pixels = Array.Empty<byte>();

            for (int r = 0; r < Height; r++)
            {
                for (int c = 0; c < Width; c++)
                {
                    int srcIdx = r * Width + c;
                    int dstRow = Width - 1 - c;
                    int dstCol = r;
                    int dstIdx = dstRow * newW + dstCol;
                    result.RedChannel[dstIdx] = RedChannel![srcIdx];
                    result.GreenChannel[dstIdx] = GreenChannel![srcIdx];
                    result.BlueChannel[dstIdx] = BlueChannel![srcIdx];
                }
            }
        }
        else
        {
            result.Pixels = new byte[newW * newH];
            for (int r = 0; r < Height; r++)
            {
                for (int c = 0; c < Width; c++)
                {
                    int dstRow = Width - 1 - c;
                    int dstCol = r;
                    result.Pixels[dstRow * newW + dstCol] = Pixels[r * Width + c];
                }
            }
        }

        return result;
    }

    /// <summary>
    /// Rotate the image 180°. Returns a NEW image (dimensions unchanged).
    /// transform completion.
    /// </summary>
    public NetpbmImage Rotate180()
    {
        var result = new NetpbmImage
        {
            Format = Format,
            Width = Width,
            Height = Height,
            MaxValue = MaxValue,
            SourcePath = SourcePath
        };
        result.Comments.AddRange(Comments);

        int len = Width * Height;

        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
        {
            result.RedChannel = new byte[len];
            result.GreenChannel = new byte[len];
            result.BlueChannel = new byte[len];
            result.Pixels = Array.Empty<byte>();

            for (int i = 0; i < len; i++)
            {
                int mirrorIdx = len - 1 - i;
                result.RedChannel[i] = RedChannel![mirrorIdx];
                result.GreenChannel[i] = GreenChannel![mirrorIdx];
                result.BlueChannel[i] = BlueChannel![mirrorIdx];
            }
        }
        else
        {
            result.Pixels = new byte[len];
            for (int i = 0; i < len; i++)
            {
                result.Pixels[i] = Pixels[len - 1 - i];
            }
        }

        return result;
    }

    /// <summary>
    /// Extract a rectangular sub-region. Returns a NEW image.
    /// crop API.
    /// </summary>
    public NetpbmImage Crop(int top, int left, int cropHeight, int cropWidth)
    {
        if (top < 0 || left < 0 || cropHeight <= 0 || cropWidth <= 0)
            throw new ArgumentOutOfRangeException("Crop dimensions must be positive.");
        if (top + cropHeight > Height || left + cropWidth > Width)
            throw new ArgumentOutOfRangeException("Crop region exceeds image bounds.");

        var result = new NetpbmImage
        {
            Format = Format,
            Width = cropWidth,
            Height = cropHeight,
            MaxValue = MaxValue,
            SourcePath = SourcePath
        };
        result.Comments.AddRange(Comments);

        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
        {
            int len = cropWidth * cropHeight;
            result.RedChannel = new byte[len];
            result.GreenChannel = new byte[len];
            result.BlueChannel = new byte[len];
            result.Pixels = Array.Empty<byte>();

            for (int r = 0; r < cropHeight; r++)
            {
                int srcBase = (top + r) * Width + left;
                int dstBase = r * cropWidth;
                Array.Copy(RedChannel!, srcBase, result.RedChannel, dstBase, cropWidth);
                Array.Copy(GreenChannel!, srcBase, result.GreenChannel, dstBase, cropWidth);
                Array.Copy(BlueChannel!, srcBase, result.BlueChannel, dstBase, cropWidth);
            }
        }
        else
        {
            result.Pixels = new byte[cropWidth * cropHeight];
            for (int r = 0; r < cropHeight; r++)
            {
                Array.Copy(Pixels, (top + r) * Width + left, result.Pixels, r * cropWidth, cropWidth);
            }
        }

        return result;
    }

    /// <summary>
    /// Create a new image resized to the specified dimensions using nearest-neighbor interpolation.
    /// basic resize for image processing pipeline.
    /// </summary>
    public NetpbmImage Resize(int newWidth, int newHeight)
    {
        if (newWidth <= 0) throw new ArgumentOutOfRangeException(nameof(newWidth), "Width must be positive.");
        if (newHeight <= 0) throw new ArgumentOutOfRangeException(nameof(newHeight), "Height must be positive.");

        var result = new NetpbmImage
        {
            Format = Format,
            Width = newWidth,
            Height = newHeight,
            MaxValue = MaxValue,
        };

        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
        {
            result.RedChannel = new byte[newWidth * newHeight];
            result.GreenChannel = new byte[newWidth * newHeight];
            result.BlueChannel = new byte[newWidth * newHeight];
            for (int row = 0; row < newHeight; row++)
            {
                int srcRow = (int)((long)row * Height / newHeight);
                if (srcRow >= Height) srcRow = Height - 1;
                for (int col = 0; col < newWidth; col++)
                {
                    int srcCol = (int)((long)col * Width / newWidth);
                    if (srcCol >= Width) srcCol = Width - 1;
                    int srcIdx = srcRow * Width + srcCol;
                    int dstIdx = row * newWidth + col;
                    result.RedChannel[dstIdx] = RedChannel![srcIdx];
                    result.GreenChannel[dstIdx] = GreenChannel![srcIdx];
                    result.BlueChannel[dstIdx] = BlueChannel![srcIdx];
                }
            }
        }
        else
        {
            result.Pixels = new byte[newWidth * newHeight];
            for (int row = 0; row < newHeight; row++)
            {
                int srcRow = (int)((long)row * Height / newHeight);
                if (srcRow >= Height) srcRow = Height - 1;
                for (int col = 0; col < newWidth; col++)
                {
                    int srcCol = (int)((long)col * Width / newWidth);
                    if (srcCol >= Width) srcCol = Width - 1;
                    result.Pixels[row * newWidth + col] = Pixels[srcRow * Width + srcCol];
                }
            }
        }
        return result;
    }

    /// <summary>
    /// Transpose the image: swap rows and columns (flip along main diagonal).
    /// diagonal flip for image transformation.
    /// </summary>
    public NetpbmImage FlipDiagonal()
    {
        var result = new NetpbmImage
        {
            Format = Format,
            Width = Height,
            Height = Width,
            MaxValue = MaxValue,
            SourcePath = SourcePath
        };
        result.Comments.AddRange(Comments);

        int newW = Height;
        int newH = Width;

        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
        {
            int len = newW * newH;
            result.RedChannel = new byte[len];
            result.GreenChannel = new byte[len];
            result.BlueChannel = new byte[len];
            result.Pixels = Array.Empty<byte>();

            for (int r = 0; r < Height; r++)
            {
                for (int c = 0; c < Width; c++)
                {
                    int srcIdx = r * Width + c;
                    int dstIdx = c * newW + r;
                    result.RedChannel[dstIdx] = RedChannel![srcIdx];
                    result.GreenChannel[dstIdx] = GreenChannel![srcIdx];
                    result.BlueChannel[dstIdx] = BlueChannel![srcIdx];
                }
            }
        }
        else
        {
            result.Pixels = new byte[newW * newH];
            for (int r = 0; r < Height; r++)
            {
                for (int c = 0; c < Width; c++)
                {
                    result.Pixels[c * newW + r] = Pixels[r * Width + c];
                }
            }
        }

        return result;
    }

    /// <summary>
    /// Merge another image horizontally (place <paramref name="other"/> to the right).
    /// Both images must have the same Height and Format. Returns a NEW image.
    /// image composition for tiling/panorama workflows.
    /// </summary>
    public NetpbmImage MergeHorizontal(NetpbmImage other)
    {
        if (other is null) throw new ArgumentNullException(nameof(other));
        if (other.Height != Height)
            throw new ArgumentException($"Height mismatch: {Height} vs {other.Height}.", nameof(other));
        if (other.Format != Format)
            throw new ArgumentException($"Format mismatch: {Format} vs {other.Format}.", nameof(other));

        int newW = Width + other.Width;
        var result = new NetpbmImage
        {
            Format = Format,
            Width = newW,
            Height = Height,
            MaxValue = Math.Max(MaxValue, other.MaxValue),
            SourcePath = SourcePath
        };
        result.Comments.AddRange(Comments);

        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
        {
            int len = newW * Height;
            result.RedChannel = new byte[len];
            result.GreenChannel = new byte[len];
            result.BlueChannel = new byte[len];
            result.Pixels = Array.Empty<byte>();

            for (int r = 0; r < Height; r++)
            {
                for (int c = 0; c < Width; c++)
                {
                    int dstIdx = r * newW + c;
                    int srcIdx = r * Width + c;
                    result.RedChannel[dstIdx] = RedChannel![srcIdx];
                    result.GreenChannel[dstIdx] = GreenChannel![srcIdx];
                    result.BlueChannel[dstIdx] = BlueChannel![srcIdx];
                }
                for (int c = 0; c < other.Width; c++)
                {
                    int dstIdx = r * newW + Width + c;
                    int srcIdx = r * other.Width + c;
                    result.RedChannel[dstIdx] = other.RedChannel![srcIdx];
                    result.GreenChannel[dstIdx] = other.GreenChannel![srcIdx];
                    result.BlueChannel[dstIdx] = other.BlueChannel![srcIdx];
                }
            }
        }
        else
        {
            result.Pixels = new byte[newW * Height];
            for (int r = 0; r < Height; r++)
            {
                for (int c = 0; c < Width; c++)
                    result.Pixels[r * newW + c] = Pixels[r * Width + c];
                for (int c = 0; c < other.Width; c++)
                    result.Pixels[r * newW + Width + c] = other.Pixels[r * other.Width + c];
            }
        }
        return result;
    }

    /// <summary>
    /// Merge another image vertically (place <paramref name="other"/> below).
    /// Both images must have the same Width and Format. Returns a NEW image.
    /// image composition for vertical tiling/stacking workflows.
    /// </summary>
    public NetpbmImage MergeVertical(NetpbmImage other)
    {
        if (other is null) throw new ArgumentNullException(nameof(other));
        if (other.Width != Width)
            throw new ArgumentException($"Width mismatch: {Width} vs {other.Width}.", nameof(other));
        if (other.Format != Format)
            throw new ArgumentException($"Format mismatch: {Format} vs {other.Format}.", nameof(other));

        int newH = Height + other.Height;
        var result = new NetpbmImage
        {
            Format = Format,
            Width = Width,
            Height = newH,
            MaxValue = Math.Max(MaxValue, other.MaxValue),
            SourcePath = SourcePath
        };
        result.Comments.AddRange(Comments);

        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
        {
            int len = Width * newH;
            result.RedChannel = new byte[len];
            result.GreenChannel = new byte[len];
            result.BlueChannel = new byte[len];
            result.Pixels = Array.Empty<byte>();

            int topLen = Width * Height;
            Array.Copy(RedChannel!, 0, result.RedChannel, 0, topLen);
            Array.Copy(GreenChannel!, 0, result.GreenChannel, 0, topLen);
            Array.Copy(BlueChannel!, 0, result.BlueChannel, 0, topLen);
            int bottomLen = Width * other.Height;
            Array.Copy(other.RedChannel!, 0, result.RedChannel, topLen, bottomLen);
            Array.Copy(other.GreenChannel!, 0, result.GreenChannel, topLen, bottomLen);
            Array.Copy(other.BlueChannel!, 0, result.BlueChannel, topLen, bottomLen);
        }
        else
        {
            int topLen = Width * Height;
            int bottomLen = Width * other.Height;
            result.Pixels = new byte[topLen + bottomLen];
            Array.Copy(Pixels, 0, result.Pixels, 0, topLen);
            Array.Copy(other.Pixels, 0, result.Pixels, topLen, bottomLen);
        }
        return result;
    }

    /// <summary>
    /// Overlay another image on top of this image at the given offset.
    /// image compositing for editing workflows.
    /// </summary>
    public NetpbmImage Overlay(NetpbmImage overlay, int topOffset, int leftOffset)
    {
        if (overlay.Format != Format)
            throw new InvalidOperationException("Overlay format must match base image format.");
        if (topOffset < 0 || leftOffset < 0)
            throw new ArgumentOutOfRangeException("Offsets must not be negative.");

        var result = Clone();

        int overlapTop = topOffset;
        int overlapLeft = leftOffset;
        int overlapBottom = Math.Min(Height, topOffset + overlay.Height);
        int overlapRight = Math.Min(Width, leftOffset + overlay.Width);

        if (overlapTop >= overlapBottom || overlapLeft >= overlapRight)
            return result; // No overlap

        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
        {
            for (int r = overlapTop; r < overlapBottom; r++)
            {
                for (int c = overlapLeft; c < overlapRight; c++)
                {
                    int srcIdx = (r - topOffset) * overlay.Width + (c - leftOffset);
                    int dstIdx = r * Width + c;
                    result.RedChannel![dstIdx] = overlay.RedChannel![srcIdx];
                    result.GreenChannel![dstIdx] = overlay.GreenChannel![srcIdx];
                    result.BlueChannel![dstIdx] = overlay.BlueChannel![srcIdx];
                }
            }
        }
        else
        {
            for (int r = overlapTop; r < overlapBottom; r++)
            {
                for (int c = overlapLeft; c < overlapRight; c++)
                {
                    int srcIdx = (r - topOffset) * overlay.Width + (c - leftOffset);
                    int dstIdx = r * Width + c;
                    result.Pixels[dstIdx] = overlay.Pixels[srcIdx];
                }
            }
        }

        return result;
    }

    /// <summary>
    /// Create a tiled image by repeating this image in an NxM grid.
    /// R113: governed /add-dotnet-api.
    /// </summary>
    public NetpbmImage Tile(int tilesX, int tilesY)
    {
        if (tilesX < 1) throw new ArgumentOutOfRangeException(nameof(tilesX), "Must be >= 1.");
        if (tilesY < 1) throw new ArgumentOutOfRangeException(nameof(tilesY), "Must be >= 1.");

        int newW = Width * tilesX;
        int newH = Height * tilesY;
        int bpp = IsPpm(Format) ? 3 : 1;

        var result = new NetpbmImage
        {
            Format = Format,
            Width = newW,
            Height = newH,
            MaxValue = MaxValue,
            Pixels = new byte[newW * newH * bpp]
        };
        if (IsPpm(Format))
        {
            result.RedChannel = new byte[newW * newH];
            result.GreenChannel = new byte[newW * newH];
            result.BlueChannel = new byte[newW * newH];
        }

        for (int ty = 0; ty < tilesY; ty++)
        for (int tx = 0; tx < tilesX; tx++)
        {
            for (int y = 0; y < Height; y++)
            for (int x = 0; x < Width; x++)
            {
                int dstY = ty * Height + y;
                int dstX = tx * Width + x;
                if (IsPpm(Format))
                {
                    int srcIdx = y * Width + x;
                    int dstIdx = dstY * newW + dstX;
                    if (RedChannel != null)
                    {
                        result.RedChannel![dstIdx] = RedChannel[srcIdx];
                        result.GreenChannel![dstIdx] = GreenChannel![srcIdx];
                        result.BlueChannel![dstIdx] = BlueChannel![srcIdx];
                    }
                    result.Pixels[dstIdx * 3] = Pixels[srcIdx * 3];
                    result.Pixels[dstIdx * 3 + 1] = Pixels[srcIdx * 3 + 1];
                    result.Pixels[dstIdx * 3 + 2] = Pixels[srcIdx * 3 + 2];
                }
                else
                {
                    result.Pixels[dstY * newW + dstX] = Pixels[y * Width + x];
                }
            }
        }
        return result;
    }
}
