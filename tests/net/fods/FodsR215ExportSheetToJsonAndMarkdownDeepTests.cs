// Tests for FodsDocument.ExportSheetToJson, ExportSheetToMarkdown deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R215

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R215: Tests for FodsDocument.ExportSheetToJson, ExportSheetToMarkdown deeper.
/// ExportSheetToJson(sheet): exports the sheet data as a JSON string.
/// ExportSheetToMarkdown(sheet): exports the sheet data as a Markdown table string.
/// Covers: ExportSheetToJson non-null; ExportSheetToJson non-empty;
/// ExportSheetToJson contains header names; ExportSheetToJson contains data values;
/// ExportSheetToJson after SetCellValue reflects change; ExportSheetToMarkdown non-null;
/// ExportSheetToMarkdown non-empty; ExportSheetToMarkdown contains header names;
/// ExportSheetToMarkdown has pipe characters (table); ExportSheetToMarkdown contains data;
/// ExportSheetToMarkdown after mutation reflects change;
/// dogfood CreateEmpty->AddSheet->Populate->ExportJson->ExportMarkdown->Mutate->Verify pipeline.
/// </summary>
public class FodsR215ExportSheetToJsonAndMarkdownDeepTests
{
    private static FodsDocument CreatePopulated()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sales");
        doc.SetCellValue("Sales", 0, 0, "Product");
        doc.SetCellValue("Sales", 0, 1, "Units");
        doc.SetCellValue("Sales", 0, 2, "Revenue");
        doc.SetCellValue("Sales", 1, 0, "Widget");
        doc.SetCellValue("Sales", 1, 1, "150");
        doc.SetCellValue("Sales", 1, 2, "1500");
        doc.SetCellValue("Sales", 2, 0, "Gadget");
        doc.SetCellValue("Sales", 2, 1, "75");
        doc.SetCellValue("Sales", 2, 2, "1875");
        return doc;
    }

    // -------------------------------------------------------------------------
    // ExportSheetToJson
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToJson_NonNull()
    {
        var doc = CreatePopulated();
        Assert.NotNull(doc.ExportSheetToJson("Sales"));
    }

    [Fact]
    public void ExportSheetToJson_NonEmpty()
    {
        var doc = CreatePopulated();
        Assert.NotEmpty(doc.ExportSheetToJson("Sales"));
    }

    [Fact]
    public void ExportSheetToJson_ContainsHeaderNames()
    {
        var doc = CreatePopulated();
        var json = doc.ExportSheetToJson("Sales");
        Assert.Contains("Product", json);
        Assert.Contains("Units", json);
    }

    [Fact]
    public void ExportSheetToJson_ContainsDataValues()
    {
        var doc = CreatePopulated();
        var json = doc.ExportSheetToJson("Sales");
        Assert.Contains("Widget", json);
        Assert.Contains("Gadget", json);
    }

    [Fact]
    public void ExportSheetToJson_AfterSetCellValue_ReflectsChange()
    {
        var doc = CreatePopulated();
        doc.SetCellValue("Sales", 1, 0, "SuperWidget");
        var json = doc.ExportSheetToJson("Sales");
        Assert.Contains("SuperWidget", json);
        Assert.DoesNotContain("\"Widget\"", json.Replace("SuperWidget", ""));
    }

    [Fact]
    public void ExportSheetToJson_MultipleSheets_Isolated()
    {
        var doc = CreatePopulated();
        doc.AddSheet("Costs");
        doc.SetCellValue("Costs", 0, 0, "Item");
        doc.SetCellValue("Costs", 1, 0, "Office Supplies");
        var salesJson = doc.ExportSheetToJson("Sales");
        var costsJson = doc.ExportSheetToJson("Costs");
        Assert.Contains("Widget", salesJson);
        Assert.DoesNotContain("Widget", costsJson);
        Assert.Contains("Office Supplies", costsJson);
    }

    // -------------------------------------------------------------------------
    // ExportSheetToMarkdown
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToMarkdown_NonNull()
    {
        var doc = CreatePopulated();
        Assert.NotNull(doc.ExportSheetToMarkdown("Sales"));
    }

    [Fact]
    public void ExportSheetToMarkdown_NonEmpty()
    {
        var doc = CreatePopulated();
        Assert.NotEmpty(doc.ExportSheetToMarkdown("Sales"));
    }

    [Fact]
    public void ExportSheetToMarkdown_ContainsHeaderNames()
    {
        var doc = CreatePopulated();
        var md = doc.ExportSheetToMarkdown("Sales");
        Assert.Contains("Product", md);
        Assert.Contains("Revenue", md);
    }

    [Fact]
    public void ExportSheetToMarkdown_HasPipeCharacters()
    {
        var doc = CreatePopulated();
        var md = doc.ExportSheetToMarkdown("Sales");
        Assert.Contains("|", md);
    }

    [Fact]
    public void ExportSheetToMarkdown_ContainsDataValues()
    {
        var doc = CreatePopulated();
        var md = doc.ExportSheetToMarkdown("Sales");
        Assert.Contains("Widget", md);
        Assert.Contains("1875", md);
    }

    [Fact]
    public void ExportSheetToMarkdown_AfterMutation_ReflectsChange()
    {
        var doc = CreatePopulated();
        doc.SetCellValue("Sales", 2, 0, "MegaGadget");
        var md = doc.ExportSheetToMarkdown("Sales");
        Assert.Contains("MegaGadget", md);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateEmpty_AddSheet_Populate_ExportJson_ExportMarkdown_Mutate_Verify_Pipeline()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Inventory");

        // Populate
        doc.SetCellValue("Inventory", 0, 0, "SKU");
        doc.SetCellValue("Inventory", 0, 1, "Item");
        doc.SetCellValue("Inventory", 0, 2, "Stock");
        doc.SetCellValue("Inventory", 1, 0, "A001");
        doc.SetCellValue("Inventory", 1, 1, "Widget");
        doc.SetCellValue("Inventory", 1, 2, "100");
        doc.SetCellValue("Inventory", 2, 0, "B002");
        doc.SetCellValue("Inventory", 2, 1, "Gadget");
        doc.SetCellValue("Inventory", 2, 2, "50");

        // ExportSheetToJson
        var json = doc.ExportSheetToJson("Inventory");
        Assert.NotEmpty(json);
        Assert.Contains("SKU", json);
        Assert.Contains("Widget", json);

        // ExportSheetToMarkdown
        var md = doc.ExportSheetToMarkdown("Inventory");
        Assert.NotEmpty(md);
        Assert.Contains("SKU", md);
        Assert.Contains("|", md);
        Assert.Contains("Widget", md);

        // Mutate and re-export
        doc.SetCellValue("Inventory", 1, 2, "120"); // stock update
        var jsonAfter = doc.ExportSheetToJson("Inventory");
        Assert.Contains("120", jsonAfter);
        var mdAfter = doc.ExportSheetToMarkdown("Inventory");
        Assert.Contains("120", mdAfter);

        // Add new row and verify
        doc.InsertRowWithValues("Inventory", 3,
            new System.Collections.Generic.List<string> { "C003", "Gizmo", "75" });
        var jsonFinal = doc.ExportSheetToJson("Inventory");
        Assert.Contains("Gizmo", jsonFinal);
        var mdFinal = doc.ExportSheetToMarkdown("Inventory");
        Assert.Contains("Gizmo", mdFinal);
    }
}
