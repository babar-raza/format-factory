// FormatFactory.Ndjson — .NET Consumer Roundtrip Proof
// Demonstrates behavioral query methods: GetAllKeys, Filter, GetFieldValues, IsUniformSchema
//
// Run with: dotnet-script examples/dotnet/ndjson/consumer_roundtrip.csx

#r "src/net/ndjson/bin/Debug/net10.0/FormatFactory.Ndjson.dll"

using FormatFactory.Ndjson;
using System;
using System.IO;
using System.Linq;
using System.Text.Json;

var samplePath = "samples/by-format/ndjson/valid/minimal.ndjson";
Console.WriteLine($"Source: {samplePath}");
Console.WriteLine();

// Step 1: Load
var doc = NdjsonDocument.LoadFile(samplePath);
Console.WriteLine($"[LOAD] Count={doc.Count}");
if (doc.Count != 3) throw new Exception($"Expected 3 records, got {doc.Count}");

// Step 2: GetAllKeys
var keys = doc.GetAllKeys();
Console.WriteLine($"[KEYS] Keys: [{string.Join(", ", keys)}]");
if (!keys.Contains("name")) throw new Exception("Expected 'name' key");
if (!keys.Contains("score")) throw new Exception("Expected 'score' key");
if (!keys.Contains("active")) throw new Exception("Expected 'active' key");

// Step 3: GetFieldValues
var names = doc.GetFieldValues("name");
Console.WriteLine($"[FIELD_VALUES] names: [{string.Join(", ", names)}]");
if (!names.Contains("Alice")) throw new Exception("Expected Alice in names");
if (!names.Contains("Bob")) throw new Exception("Expected Bob in names");

// Step 4: IsUniformSchema
var uniform = doc.IsUniformSchema();
Console.WriteLine($"[SCHEMA] IsUniformSchema={uniform}");
if (!uniform) throw new Exception("Expected uniform schema (all records have same keys)");

// Step 5: Filter
var active = doc.Filter(rec => {
    if (rec.TryGetProperty("active", out var prop))
        return prop.GetBoolean();
    return false;
});
Console.WriteLine($"[FILTER] Active records: {active.Count}");
if (active.Count != 2) throw new Exception($"Expected 2 active records (Alice, Carol), got {active.Count}");

// Step 6: Filter by score
var highScorers = doc.Filter(rec => {
    if (rec.TryGetProperty("score", out var prop))
        return prop.GetInt32() >= 90;
    return false;
});
Console.WriteLine($"[FILTER] High scorers (>=90): {highScorers.Count}");
if (highScorers.Count != 2) throw new Exception($"Expected 2 high scorers (Alice=95, Carol=91), got {highScorers.Count}");

Console.WriteLine();
Console.WriteLine("CONSUMER_PROOF: PASS -- load -> GetAllKeys -> GetFieldValues -> IsUniformSchema -> Filter");
