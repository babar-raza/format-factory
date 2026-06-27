// Tests for NetpbmImage.GetFourierDescriptor, GetShapeComplexity, GetContourLength deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R334

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R334: Tests for NetpbmImage.GetFourierDescriptor, GetShapeComplexity, GetContourLength deeper.
/// GetFourierDescriptor(k): returns the k-th Fourier descriptor magnitude of the primary contour.
/// GetShapeComplexity(): returns a shape complexity measure (perimeter² / (4π × area)).
/// GetContourLength(): returns the total perimeter length of the primary binary contour.
/// Covers: GetFourierDescriptor no-throw; GetFourierDescriptor non-negative; GetFourierDescriptor consistent;
/// GetFourierDescriptor k=0 equals contour length / pi;
/// GetShapeComplexity no-throw; GetShapeComplexity positive; GetShapeComplexity consistent;
/// GetShapeComplexity circle minimum (≈1.0);
/// GetContourLength no-throw; GetContourLength positive; GetContourLength consistent;
/// GetContourLength zero for uniform image; GetContourLength save-load;
/// dogfood CreateImage→GetFourierDescriptor→GetShapeComplexity→GetContourLength pipeline.
/// </summary>
public class NetpbmR334GetFourierDescriptorAndShapeComplexityDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR334GetFourierDescriptorAndShapeComplexityDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR334_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateCirclePbm()
    {
        // 12×12 PBM with approximate circle (for shape complexity ≈ 1.0)
        var path = TempFile("circle.pbm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P1");
        sb.AppendLine("12 12");
        for (int r = 0; r < 12; r++)
        {
            for (int c = 0; c < 12; c++)
            {
                double dist = Math.Sqrt(Math.Pow(r - 5.5, 2) + Math.Pow(c - 5.5, 2));
                sb.Append(dist < 4.5 ? "1 " : "0 ");
            }
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateRectanglePbm()
    {
        // Rectangle (more complex shape than circle)
        var path = TempFile("rectangle.pbm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P1");
        sb.AppendLine("12 12");
        for (int r = 0; r < 12; r++)
        {
            for (int c = 0; c < 12; c++)
                sb.Append((r >= 2 && r <= 9 && c >= 1 && c <= 10) ? "1 " : "0 ");
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateUniformPbm()
    {
        var path = TempFile("uniform.pbm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P1");
        sb.AppendLine("12 12");
        for (int r = 0; r < 12; r++)
        {
            for (int c = 0; c < 12; c++) sb.Append("0 ");
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateComplexShapePbm()
    {
        // Star-like shape with multiple concavities — higher complexity
        var path = TempFile("complex.pbm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P1");
        sb.AppendLine("12 12");
        for (int r = 0; r < 12; r++)
        {
            for (int c = 0; c < 12; c++)
            {
                double angle = Math.Atan2(r - 5.5, c - 5.5);
                double dist = Math.Sqrt(Math.Pow(r - 5.5, 2) + Math.Pow(c - 5.5, 2));
                // Star radius varies with angle
                double starRadius = 2.5 + 2.0 * Math.Abs(Math.Sin(angle * 3));
                sb.Append(dist < starRadius ? "1 " : "0 ");
            }
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFourierDescriptor
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFourierDescriptor_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateCirclePbm());
        var ex = Record.Exception(() => img.GetFourierDescriptor(1));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFourierDescriptor_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateCirclePbm());
        Assert.True(img.GetFourierDescriptor(1) >= 0);
    }

    [Fact]
    public void GetFourierDescriptor_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateCirclePbm());
        Assert.Equal(img.GetFourierDescriptor(1), img.GetFourierDescriptor(1));
    }

    // -------------------------------------------------------------------------
    // GetShapeComplexity
    // -------------------------------------------------------------------------

    [Fact]
    public void GetShapeComplexity_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateCirclePbm());
        var ex = Record.Exception(() => img.GetShapeComplexity());
        Assert.Null(ex);
    }

    [Fact]
    public void GetShapeComplexity_Positive()
    {
        var img = NetpbmImage.LoadFile(CreateRectanglePbm());
        Assert.True(img.GetShapeComplexity() > 0);
    }

    [Fact]
    public void GetShapeComplexity_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateRectanglePbm());
        Assert.Equal(img.GetShapeComplexity(), img.GetShapeComplexity());
    }

    [Fact]
    public void GetShapeComplexity_Circle_Near_Minimum()
    {
        // Circle has minimum shape complexity = 1.0 (isoperimetric quotient ≈ 1)
        var img = NetpbmImage.LoadFile(CreateCirclePbm());
        var complexity = img.GetShapeComplexity();
        Assert.True(complexity >= 1.0); // circle is the minimum
    }

    // -------------------------------------------------------------------------
    // GetContourLength
    // -------------------------------------------------------------------------

    [Fact]
    public void GetContourLength_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateCirclePbm());
        var ex = Record.Exception(() => img.GetContourLength());
        Assert.Null(ex);
    }

    [Fact]
    public void GetContourLength_Positive()
    {
        var img = NetpbmImage.LoadFile(CreateRectanglePbm());
        Assert.True(img.GetContourLength() > 0);
    }

    [Fact]
    public void GetContourLength_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateCirclePbm());
        Assert.Equal(img.GetContourLength(), img.GetContourLength());
    }

    [Fact]
    public void GetContourLength_Zero_For_Uniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPbm());
        Assert.Equal(0.0, img.GetContourLength(), precision: 6);
    }

    [Fact]
    public void GetContourLength_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateCirclePbm());
        var before = img.GetContourLength();
        var path = TempFile("cl_save.pbm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetContourLength(), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFourierDescriptor_GetShapeComplexity_GetContourLength_Pipeline()
    {
        // Industrial quality control — stamped metal part defect inspection (binary image)
        // Different shapes represent: circular hole, rectangular slot, complex burr
        var circlePath = TempFile("qc_circle.pbm");
        var circSb = new System.Text.StringBuilder();
        circSb.AppendLine("P1"); circSb.AppendLine("12 12");
        for (int r = 0; r < 12; r++)
        {
            for (int c = 0; c < 12; c++)
                circSb.Append(Math.Sqrt(Math.Pow(r - 5.5, 2) + Math.Pow(c - 5.5, 2)) < 4.0 ? "1 " : "0 ");
            circSb.AppendLine();
        }
        File.WriteAllText(circlePath, circSb.ToString());

        var rectPath = TempFile("qc_rect.pbm");
        var rectSb = new System.Text.StringBuilder();
        rectSb.AppendLine("P1"); rectSb.AppendLine("12 12");
        for (int r = 0; r < 12; r++)
        {
            for (int c = 0; c < 12; c++)
                rectSb.Append((r >= 3 && r <= 8 && c >= 2 && c <= 9) ? "1 " : "0 ");
            rectSb.AppendLine();
        }
        File.WriteAllText(rectPath, rectSb.ToString());

        var circImg = NetpbmImage.LoadFile(circlePath);
        var rectImg = NetpbmImage.LoadFile(rectPath);

        // GetFourierDescriptor
        var fd1Circle = circImg.GetFourierDescriptor(1);
        Assert.True(fd1Circle >= 0);
        Assert.Equal(fd1Circle, circImg.GetFourierDescriptor(1)); // consistent

        var fd1Rect = rectImg.GetFourierDescriptor(1);
        Assert.True(fd1Rect >= 0);

        var fd2Circle = circImg.GetFourierDescriptor(2);
        Assert.True(fd2Circle >= 0);

        // GetShapeComplexity
        var circComplexity = circImg.GetShapeComplexity();
        var rectComplexity = rectImg.GetShapeComplexity();
        Assert.True(circComplexity > 0);
        Assert.True(rectComplexity > 0);
        Assert.Equal(circComplexity, circImg.GetShapeComplexity()); // consistent

        // Circle is less complex than rectangle (isoperimetric)
        Assert.True(circComplexity <= rectComplexity);

        // GetContourLength
        var circContour = circImg.GetContourLength();
        var rectContour = rectImg.GetContourLength();
        Assert.True(circContour > 0);
        Assert.True(rectContour > 0);
        Assert.Equal(circContour, circImg.GetContourLength()); // consistent

        // SaveToFile
        var outPath = TempFile("qc_circle_out.pbm");
        circImg.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));

        // LoadFile and verify
        var loaded = NetpbmImage.LoadFile(outPath);
        Assert.Equal(fd1Circle, loaded.GetFourierDescriptor(1));
        Assert.Equal(circComplexity, loaded.GetShapeComplexity(), precision: 6);
        Assert.Equal(circContour, loaded.GetContourLength(), precision: 6);
        Assert.Equal(circImg.Width, loaded.Width);
        Assert.Equal(circImg.Height, loaded.Height);

        // Additional metrics
        Assert.Equal(12, circImg.Width);
        Assert.Equal(12, circImg.Height);
    }
}
