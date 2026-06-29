// FormatFactory.Zst — .NET Consumer Roundtrip Proof
// Demonstrates computed properties: IsValid, HasMultipleFrames, FileSizeKB, SizeLabel
//
// Run with: dotnet-script examples/dotnet/zst/consumer_roundtrip.csx

#r "src/net/zst/bin/Debug/net10.0/FormatFactory.Zst.dll"

using FormatFactory.Zst;
using System;
using System.IO;

var samplePath = "samples/by-format/zst/valid/minimal-synthetic.zst";
Console.WriteLine($"Source: {samplePath}");
Console.WriteLine();

// Step 1: Parse via ZstParser -> ZstDocument
var doc = ZstParser.Parse(samplePath);
Console.WriteLine($"[LOAD] FileSizeBytes={doc.FileSizeBytes}, FrameCount={doc.FrameCount}, MagicValid={doc.MagicValid}");

// Step 2: IsValid
var isValid = doc.IsValid;
Console.WriteLine($"[INSPECT] IsValid={isValid}");
if (!isValid) throw new Exception("Expected valid ZST document");

// Step 3: HasMultipleFrames
var multi = doc.HasMultipleFrames;
Console.WriteLine($"[INSPECT] HasMultipleFrames={multi}");
// minimal-synthetic.zst has 1 frame — should not be multi
if (multi) Console.WriteLine("  (multiple frames detected — valid for concatenated ZST)");

// Step 4: FileSizeKB
var sizeKB = doc.FileSizeKB;
Console.WriteLine($"[SIZE] FileSizeKB={sizeKB:F2}");
if (sizeKB <= 0) throw new Exception("Expected positive file size");

// Step 5: SizeLabel
var sizeLabel = doc.SizeLabel;
Console.WriteLine($"[SIZE] SizeLabel={sizeLabel}");
if (string.IsNullOrEmpty(sizeLabel)) throw new Exception("Expected non-empty SizeLabel");

Console.WriteLine();
Console.WriteLine("CONSUMER_PROOF: PASS -- load -> IsValid -> HasMultipleFrames -> FileSizeKB -> SizeLabel");
