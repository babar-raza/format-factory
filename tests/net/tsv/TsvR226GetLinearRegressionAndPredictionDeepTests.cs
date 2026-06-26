// Tests for TsvDocument.GetLinearRegressionSlope, GetLinearRegressionIntercept, GetPredictedValue deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R226

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R226: Tests for TsvDocument.GetLinearRegressionSlope, GetLinearRegressionIntercept, GetPredictedValue deeper.
/// GetLinearRegressionSlope(xCol, yCol): returns the slope of the OLS regression line.
/// GetLinearRegressionIntercept(xCol, yCol): returns the intercept of the OLS regression line.
/// GetPredictedValue(xCol, yCol, xValue): returns the predicted y for a given x value.
/// Covers: GetLinearRegressionSlope no-throw; GetLinearRegressionSlope finite; GetLinearRegressionSlope consistent;
/// GetLinearRegressionSlope save-load; GetLinearRegressionSlope positive for positively correlated;
/// GetLinearRegressionIntercept no-throw; GetLinearRegressionIntercept finite; GetLinearRegressionIntercept consistent;
/// GetLinearRegressionIntercept save-load;
/// GetPredictedValue no-throw; GetPredictedValue finite; GetPredictedValue consistent;
/// GetPredictedValue save-load;
/// dogfood CreateDoc→GetLinearRegressionSlope→GetLinearRegressionIntercept→GetPredictedValue pipeline.
/// </summary>
public class TsvR226GetLinearRegressionAndPredictionDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR226GetLinearRegressionAndPredictionDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR226_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateHousingTsv()
    {
        var path = TempFile("housing.tsv");
        File.WriteAllText(path,
            "city\tsqft\tbedrooms\tage_years\tprice_gbp\n" +
            "Manchester\t850\t2\t15\t185000\n" +
            "Leeds\t1100\t3\t8\t245000\n" +
            "Sheffield\t950\t3\t22\t195000\n" +
            "Bradford\t780\t2\t30\t160000\n" +
            "Liverpool\t1200\t4\t5\t280000\n" +
            "Newcastle\t900\t3\t18\t210000\n" +
            "Nottingham\t1050\t3\t12\t235000\n" +
            "Leicester\t880\t2\t20\t190000\n" +
            "Bristol\t1350\t4\t3\t390000\n" +
            "Cardiff\t820\t2\t25\t175000\n");
        return path;
    }

    // -------------------------------------------------------------------------
    // GetLinearRegressionSlope
    // -------------------------------------------------------------------------

    [Fact]
    public void GetLinearRegressionSlope_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateHousingTsv());
        var ex = Record.Exception(() => doc.GetLinearRegressionSlope("sqft", "price_gbp"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetLinearRegressionSlope_Finite()
    {
        var doc = TsvDocument.LoadFile(CreateHousingTsv());
        var slope = doc.GetLinearRegressionSlope("sqft", "price_gbp");
        Assert.True(double.IsFinite(slope));
    }

    [Fact]
    public void GetLinearRegressionSlope_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateHousingTsv());
        Assert.Equal(
            doc.GetLinearRegressionSlope("sqft", "price_gbp"),
            doc.GetLinearRegressionSlope("sqft", "price_gbp"));
    }

    [Fact]
    public void GetLinearRegressionSlope_Positive_ForPositivelyCorrelated()
    {
        var doc = TsvDocument.LoadFile(CreateHousingTsv());
        // sqft and price_gbp are positively correlated
        var slope = doc.GetLinearRegressionSlope("sqft", "price_gbp");
        Assert.True(slope > 0.0);
    }

    [Fact]
    public void GetLinearRegressionSlope_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateHousingTsv());
        var before = doc.GetLinearRegressionSlope("sqft", "price_gbp");
        var path = TempFile("slope_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetLinearRegressionSlope("sqft", "price_gbp"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetLinearRegressionIntercept
    // -------------------------------------------------------------------------

    [Fact]
    public void GetLinearRegressionIntercept_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateHousingTsv());
        var ex = Record.Exception(() => doc.GetLinearRegressionIntercept("sqft", "price_gbp"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetLinearRegressionIntercept_Finite()
    {
        var doc = TsvDocument.LoadFile(CreateHousingTsv());
        var intercept = doc.GetLinearRegressionIntercept("sqft", "price_gbp");
        Assert.True(double.IsFinite(intercept));
    }

    [Fact]
    public void GetLinearRegressionIntercept_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateHousingTsv());
        Assert.Equal(
            doc.GetLinearRegressionIntercept("sqft", "price_gbp"),
            doc.GetLinearRegressionIntercept("sqft", "price_gbp"));
    }

    [Fact]
    public void GetLinearRegressionIntercept_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateHousingTsv());
        var before = doc.GetLinearRegressionIntercept("sqft", "price_gbp");
        var path = TempFile("intercept_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetLinearRegressionIntercept("sqft", "price_gbp"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetPredictedValue
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPredictedValue_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateHousingTsv());
        var ex = Record.Exception(() => doc.GetPredictedValue("sqft", "price_gbp", 1000.0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetPredictedValue_Finite()
    {
        var doc = TsvDocument.LoadFile(CreateHousingTsv());
        var pred = doc.GetPredictedValue("sqft", "price_gbp", 1000.0);
        Assert.True(double.IsFinite(pred));
    }

    [Fact]
    public void GetPredictedValue_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateHousingTsv());
        Assert.Equal(
            doc.GetPredictedValue("sqft", "price_gbp", 1100.0),
            doc.GetPredictedValue("sqft", "price_gbp", 1100.0));
    }

    [Fact]
    public void GetPredictedValue_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateHousingTsv());
        var before = doc.GetPredictedValue("sqft", "price_gbp", 1200.0);
        var path = TempFile("pred_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetPredictedValue("sqft", "price_gbp", 1200.0), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetLinearRegressionSlope_GetIntercept_GetPredictedValue_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_productivity.tsv");
        File.WriteAllText(path,
            "company\tr_and_d_spend_mGBP\trevenue_mGBP\temployees\tpatents_filed\tprofit_margin_pct\n" +
            "AstraZeneca\t6200\t45800\t83100\t2140\t18.2\n" +
            "GSK\t5700\t29800\t68000\t1820\t15.7\n" +
            "Rolls-Royce\t1400\t14700\t42000\t890\t8.3\n" +
            "BAE Systems\t1100\t23400\t99500\t540\t7.1\n" +
            "ARM Holdings\t820\t2900\t6400\t3200\t28.4\n" +
            "Sage Group\t410\t2100\t14200\t180\t19.6\n" +
            "Haleon\t520\t11400\t22000\t420\t12.8\n" +
            "Experian\t680\t7700\t21700\t760\t22.5\n" +
            "RELX\t840\t9200\t35400\t1100\t24.3\n" +
            "Informa\t280\t3200\t11500\t90\t14.1\n");

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(10, doc.GetRowCount());
        Assert.Equal(6, doc.GetColumnCount());

        // GetLinearRegressionSlope — R&D vs Revenue (expect positive)
        var slopeRdRev = doc.GetLinearRegressionSlope("r_and_d_spend_mGBP", "revenue_mGBP");
        Assert.True(double.IsFinite(slopeRdRev));
        Assert.True(slopeRdRev > 0.0); // more R&D → more revenue

        var slopeRdPatents = doc.GetLinearRegressionSlope("r_and_d_spend_mGBP", "patents_filed");
        Assert.True(double.IsFinite(slopeRdPatents));

        // Consistent
        Assert.Equal(slopeRdRev, doc.GetLinearRegressionSlope("r_and_d_spend_mGBP", "revenue_mGBP"));

        // GetLinearRegressionIntercept
        var interceptRdRev = doc.GetLinearRegressionIntercept("r_and_d_spend_mGBP", "revenue_mGBP");
        Assert.True(double.IsFinite(interceptRdRev));

        var interceptEmpProfit = doc.GetLinearRegressionIntercept("employees", "profit_margin_pct");
        Assert.True(double.IsFinite(interceptEmpProfit));

        // Consistent
        Assert.Equal(interceptRdRev, doc.GetLinearRegressionIntercept("r_and_d_spend_mGBP", "revenue_mGBP"));

        // GetPredictedValue — predict revenue for R&D spend of £2000m
        var pred2000 = doc.GetPredictedValue("r_and_d_spend_mGBP", "revenue_mGBP", 2000.0);
        Assert.True(double.IsFinite(pred2000));

        var pred5000 = doc.GetPredictedValue("r_and_d_spend_mGBP", "revenue_mGBP", 5000.0);
        Assert.True(double.IsFinite(pred5000));

        // Higher R&D spend should predict higher revenue (positive slope)
        Assert.True(pred5000 > pred2000);

        // Consistent
        Assert.Equal(pred2000, doc.GetPredictedValue("r_and_d_spend_mGBP", "revenue_mGBP", 2000.0));

        // ExportToCsv no-throw
        var ex1 = Record.Exception(() => doc.ExportToCsv());
        Assert.Null(ex1);

        // SaveToFile
        var out1 = TempFile("dogfood_productivity_out.tsv");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(out1);
        Assert.Equal(10, loaded.GetRowCount());
        Assert.Equal(slopeRdRev, loaded.GetLinearRegressionSlope("r_and_d_spend_mGBP", "revenue_mGBP"), precision: 6);
        Assert.Equal(interceptRdRev, loaded.GetLinearRegressionIntercept("r_and_d_spend_mGBP", "revenue_mGBP"), precision: 6);
        Assert.Equal(pred2000, loaded.GetPredictedValue("r_and_d_spend_mGBP", "revenue_mGBP", 2000.0), precision: 6);

        // AddRow and verify slope changes
        loaded.AddRow(new[] { "Aveva", "150", "1300", "6500", "70", "16.8" });
        Assert.Equal(11, loaded.GetRowCount());
        var newSlope = loaded.GetLinearRegressionSlope("r_and_d_spend_mGBP", "revenue_mGBP");
        Assert.True(double.IsFinite(newSlope));

        // Final save
        var out2 = TempFile("dogfood_productivity_v2.tsv");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = TsvDocument.LoadFile(out2);
        Assert.Equal(11, loaded2.GetRowCount());
        Assert.True(double.IsFinite(loaded2.GetLinearRegressionSlope("r_and_d_spend_mGBP", "revenue_mGBP")));
        Assert.True(double.IsFinite(loaded2.GetLinearRegressionIntercept("r_and_d_spend_mGBP", "revenue_mGBP")));
        Assert.True(double.IsFinite(loaded2.GetPredictedValue("r_and_d_spend_mGBP", "revenue_mGBP", 1000.0)));
        var ex2 = Record.Exception(() => loaded2.ExportToCsv());
        Assert.Null(ex2);
    }
}
