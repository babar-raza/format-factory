// FormatFactory.Fods — Model.Office.Document
// spec_qname: office:document
// spec_fact_ref: FACT-FODS-001
// Authority: plans/.claude/imperative-drifting-conway.md §2, §3
// TC-W1-FODS-NET-001

using System.Collections.Generic;

namespace FormatFactory.Fods.Model.Office;

/// <summary>
/// Canonical runtime model for the ODF office:document root element.
///
/// ODF 1.3 §3.1.2 — office:document is the root element of a flat ODF file.
/// spec_qname: office:document
/// spec_fact_ref: FACT-FODS-001
///
/// This class is the parser-populated runtime model. Public API entry point:
/// <see cref="FormatFactory.Fods.FodsDocument"/> (facade).
/// </summary>
public sealed class Document
{
    /// <summary>The ODF QName for this element.</summary>
    public const string SpecQName = "office:document";

    /// <summary>The SAL fact reference (sal-facts-latest.json).</summary>
    public const string SpecFactRef = "FACT-FODS-001";

    /// <summary>
    /// The office:spreadsheet body — holds all table:table (sheet) elements.
    /// Maps to office:body/office:spreadsheet in the XML structure.
    /// </summary>
    public Spreadsheet Spreadsheet { get; set; } = new Spreadsheet();

    /// <summary>
    /// Automatic styles defined in office:automatic-styles.
    /// Keyed by style:name attribute value.
    /// </summary>
    public List<FormatFactory.Fods.Model.Style.Style> AutomaticStyles { get; } = new();

    /// <summary>office:version attribute value (e.g. "1.3").</summary>
    public string Version { get; set; } = "1.3";

    /// <summary>office:mimetype attribute value.</summary>
    public string MimeType { get; set; } =
        "application/vnd.oasis.opendocument.spreadsheet-flat-xml";
}
