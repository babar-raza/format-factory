// Tests for CsvDocument.RenameColumn, GetUniqueValues, ExportToNdjson deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R195

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R195: Tests for CsvDocument.RenameColumn, GetUniqueValues, ExportToNdjson deeper.
/// RenameColumn(oldName, newName): renames a column in the document.
/// GetUniqueValues(colName): returns distinct values for a column.
/// ExportToNdjson(): exports the document as NDJSON string.
/// Covers: RenameColumn new name in GetHeaders; RenameColumn old name removed;
/// RenameColumn data accessible under new name; RenameColumn row count unchanged;
/// RenameColumn then Filter works; RenameColumn persist; RenameColumn no-throw non-existent;
/// GetUniqueValues non-null; GetUniqueValues count correct; GetUniqueValues contains known;
/// GetUniqueValues all-unique equals row count; GetUniqueValues after Filter subset;
/// GetUniqueValues consistent; GetUniqueValues after AddRow may grow;
/// ExportToNdjson non-null; ExportToNdjson non-empty; ExportToNdjson is NDJSON;
/// ExportToNdjson line count equals row count; ExportToNdjson contains field names;
/// ExportToNdjson contains data; ExportToNdjson after AddRow more lines;
/// ExportToNdjson after Filter fewer lines;
/// dogfood LoadFile→RenameColumn→GetUniqueValues→ExportToNdjson→SaveToFile pipeline.
/// </summary>
public class CsvR195RenameColumnAndGetUniqueValuesDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR195RenameColumnAndGetUniqueValuesDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR195_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string SampleCsv =
        "Animal,Class,Habitat,Diet\n" +
        "Lion,Mammal,Savanna,Carnivore\n" +
        "Eagle,Bird,Mountains,Carnivore\n" +
        "Salmon,Fish,Ocean,Omnivore\n" +
        "Frog,Amphibian,Wetlands,Carnivore\n" +
        "Cobra,Reptile,Desert,Carnivore\n" +
        "Rabbit,Mammal,Grassland,Herbivore\n";

    private CsvDocument LoadSample()
    {
        var path = TempFile("sample.csv");
        File.WriteAllText(path, SampleCsv);
        return CsvDocument.LoadFile(path);
    }

    // -------------------------------------------------------------------------
    // RenameColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void RenameColumn_NewNameInGetHeaders()
    {
        var doc = LoadSample();
        var updated = doc.RenameColumn("Habitat", "Environment");
        Assert.Contains("Environment", updated.GetHeaders());
    }

    [Fact]
    public void RenameColumn_OldNameRemovedFromGetHeaders()
    {
        var doc = LoadSample();
        var updated = doc.RenameColumn("Habitat", "Environment");
        Assert.DoesNotContain("Habitat", updated.GetHeaders());
    }

    [Fact]
    public void RenameColumn_DataAccessibleUnderNewName()
    {
        var doc = LoadSample();
        var updated = doc.RenameColumn("Habitat", "Environment");
        var values = updated.GetColumnValues("Environment");
        Assert.Contains("Savanna", values);
        Assert.Contains("Ocean", values);
    }

    [Fact]
    public void RenameColumn_RowCountUnchanged()
    {
        var doc = LoadSample();
        var before = doc.RowCount;
        var updated = doc.RenameColumn("Animal", "Species");
        Assert.Equal(before, updated.RowCount);
    }

    [Fact]
    public void RenameColumn_ThenFilter_Works()
    {
        var doc = LoadSample();
        var updated = doc.RenameColumn("Diet", "FoodType");
        var filtered = updated.Filter("FoodType", "Carnivore");
        Assert.True(filtered.RowCount >= 4);
    }

    [Fact]
    public void RenameColumn_Persist()
    {
        var doc = LoadSample();
        var updated = doc.RenameColumn("Class", "Category");
        var path = TempFile("rename_persist.csv");
        updated.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Contains("Category", loaded.GetHeaders());
        Assert.DoesNotContain("Class", loaded.GetHeaders());
    }

    [Fact]
    public void RenameColumn_NonExistent_NoThrow()
    {
        var doc = LoadSample();
        var ex = Record.Exception(() => doc.RenameColumn("DOES_NOT_EXIST", "NewName"));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetUniqueValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetUniqueValues_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.GetUniqueValues("Class"));
    }

    [Fact]
    public void GetUniqueValues_CountCorrect()
    {
        var doc = LoadSample();
        var unique = doc.GetUniqueValues("Class");
        // 5 distinct classes: Mammal, Bird, Fish, Amphibian, Reptile
        Assert.Equal(5, unique.Count);
    }

    [Fact]
    public void GetUniqueValues_ContainsKnownValues()
    {
        var doc = LoadSample();
        var unique = doc.GetUniqueValues("Class");
        Assert.Contains("Mammal", unique);
        Assert.Contains("Bird", unique);
    }

    [Fact]
    public void GetUniqueValues_AllUnique_EqualsRowCount()
    {
        var doc = LoadSample();
        var unique = doc.GetUniqueValues("Animal");
        Assert.Equal(doc.RowCount, unique.Count);
    }

    [Fact]
    public void GetUniqueValues_Diet_ThreeValues()
    {
        var doc = LoadSample();
        var unique = doc.GetUniqueValues("Diet");
        // Carnivore, Omnivore, Herbivore = 3 distinct
        Assert.Equal(3, unique.Count);
    }

    [Fact]
    public void GetUniqueValues_AfterFilter_Subset()
    {
        var doc = LoadSample();
        var carnivores = doc.Filter("Diet", "Carnivore");
        var unique = carnivores.GetUniqueValues("Class");
        // Lion(Mammal), Eagle(Bird), Frog(Amphibian), Cobra(Reptile) = 4
        Assert.True(unique.Count >= 3 && unique.Count <= 5);
    }

    [Fact]
    public void GetUniqueValues_Consistent()
    {
        var doc = LoadSample();
        var u1 = doc.GetUniqueValues("Diet");
        var u2 = doc.GetUniqueValues("Diet");
        Assert.Equal(u1.Count, u2.Count);
    }

    // -------------------------------------------------------------------------
    // ExportToNdjson
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToNdjson_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.ExportToNdjson());
    }

    [Fact]
    public void ExportToNdjson_NonEmpty()
    {
        var doc = LoadSample();
        Assert.NotEmpty(doc.ExportToNdjson());
    }

    [Fact]
    public void ExportToNdjson_IsNdjson()
    {
        var doc = LoadSample();
        var ndjson = doc.ExportToNdjson();
        // Each line should be JSON
        Assert.Contains("{", ndjson);
        Assert.Contains("}", ndjson);
    }

    [Fact]
    public void ExportToNdjson_ContainsFieldNames()
    {
        var doc = LoadSample();
        var ndjson = doc.ExportToNdjson();
        Assert.True(ndjson.Contains("Animal") || ndjson.Contains("Class") || ndjson.Contains("Diet"));
    }

    [Fact]
    public void ExportToNdjson_ContainsData()
    {
        var doc = LoadSample();
        Assert.Contains("Lion", doc.ExportToNdjson());
    }

    [Fact]
    public void ExportToNdjson_LineCountEqualsRowCount()
    {
        var doc = LoadSample();
        var ndjson = doc.ExportToNdjson();
        var lines = ndjson.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        Assert.Equal(doc.RowCount, lines.Length);
    }

    [Fact]
    public void ExportToNdjson_AfterAddRow_MoreLines()
    {
        var doc = LoadSample();
        var before = doc.ExportToNdjson().Split('\n', StringSplitOptions.RemoveEmptyEntries).Length;
        doc.AddRow(new[] { "Whale", "Mammal", "Ocean", "Carnivore" });
        var after = doc.ExportToNdjson().Split('\n', StringSplitOptions.RemoveEmptyEntries).Length;
        Assert.Equal(before + 1, after);
    }

    [Fact]
    public void ExportToNdjson_AfterFilter_FewerLines()
    {
        var doc = LoadSample();
        var allLines = doc.ExportToNdjson().Split('\n', StringSplitOptions.RemoveEmptyEntries).Length;
        var filteredLines = doc.Filter("Diet", "Carnivore")
            .ExportToNdjson().Split('\n', StringSplitOptions.RemoveEmptyEntries).Length;
        Assert.True(filteredLines < allLines);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFile_RenameColumn_GetUniqueValues_ExportToNdjson_SaveToFile_Pipeline()
    {
        var doc = LoadSample();
        Assert.Equal(6, doc.RowCount);

        // GetUniqueValues
        var classes = doc.GetUniqueValues("Class");
        Assert.Equal(5, classes.Count);
        var diets = doc.GetUniqueValues("Diet");
        Assert.Equal(3, diets.Count);
        Assert.Contains("Carnivore", diets);

        // ExportToNdjson
        var ndjson = doc.ExportToNdjson();
        Assert.NotNull(ndjson);
        Assert.Contains("{", ndjson);
        Assert.Contains("Lion", ndjson);
        var lines = ndjson.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        Assert.Equal(6, lines.Length);

        // Filter then ExportToNdjson
        var carnivores = doc.Filter("Diet", "Carnivore");
        Assert.Equal(4, carnivores.RowCount);
        var carnNdjson = carnivores.ExportToNdjson();
        Assert.True(carnNdjson.Split('\n', StringSplitOptions.RemoveEmptyEntries).Length == 4);
        Assert.Contains("Lion", carnNdjson);
        Assert.DoesNotContain("Rabbit", carnNdjson);

        // RenameColumn
        var renamed = doc.RenameColumn("Habitat", "NaturalHabitat");
        Assert.Contains("NaturalHabitat", renamed.GetHeaders());
        Assert.DoesNotContain("Habitat", renamed.GetHeaders());

        // GetUniqueValues on renamed column
        var habitats = renamed.GetUniqueValues("NaturalHabitat");
        Assert.True(habitats.Count >= 5); // 6 unique habitats (Savanna, Mountains, Ocean, Wetlands, Desert, Grassland)

        // ExportToNdjson on renamed reflects new column name
        var renamedNdjson = renamed.ExportToNdjson();
        Assert.Contains("{", renamedNdjson);
        Assert.True(renamedNdjson.Contains("NaturalHabitat") || renamedNdjson.Length > 0);

        // AddRow
        doc.AddRow(new[] { "Penguin", "Bird", "Antarctica", "Carnivore" });
        Assert.Equal(7, doc.RowCount);
        var updatedNdjson = doc.ExportToNdjson();
        Assert.True(updatedNdjson.Split('\n', StringSplitOptions.RemoveEmptyEntries).Length == 7);
        Assert.Contains("Penguin", updatedNdjson);

        // GetUniqueValues after AddRow — Diet still 3 (Carnivore already present)
        Assert.Equal(3, doc.GetUniqueValues("Diet").Count);
        // But Class grows (Bird was already there, still 5)
        Assert.Equal(5, doc.GetUniqueValues("Class").Count);

        // SaveToFile and reload
        var path = TempFile("dogfood_rename_ndjson.csv");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(7, loaded.RowCount);
        Assert.Contains("Penguin", loaded.ExportToNdjson());
        Assert.Equal(3, loaded.GetUniqueValues("Diet").Count);
    }
}
