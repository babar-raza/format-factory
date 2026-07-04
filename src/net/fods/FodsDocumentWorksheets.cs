// FormatFactory.Fods — FodsDocumentWorksheets
// Adds the Aspose-style Worksheets property to FodsDocument.
// TC-W1-FODS-NET-003
// Authority: plans/.claude/imperative-drifting-conway.md §1, §3

using System;
using System.Xml.Linq;

namespace FormatFactory.Fods;

public sealed partial class FodsDocument
{
    // =========================================================================
    // Aspose-style Worksheets collection (TC-W1-FODS-NET-003)
    // spec_qname: office:spreadsheet (container)
    // ODF 1.3 §3.7
    // =========================================================================

    /// <summary>
    /// Aspose-style collection of all worksheets in this document.
    ///
    /// Access worksheets by index or name:
    ///   doc.Worksheets[0]
    ///   doc.Worksheets["Sheet1"]
    ///   doc.Worksheets.Count
    ///   doc.Worksheets.Add("New")
    ///   doc.Worksheets.Remove("Old")
    ///
    /// Canonical model: <see cref="FormatFactory.Fods.Model.Office.Spreadsheet"/>
    /// spec_qname: office:spreadsheet
    /// ODF 1.3 §3.7, §9.1.2
    /// </summary>
    public FodsWorksheetCollection Worksheets
    {
        get
        {
            var body = _doc.Root?.Element(NsOffice + "body");
            var spreadsheet = body?.Element(NsOffice + "spreadsheet");
            if (spreadsheet is null)
                throw new InvalidOperationException(
                    "Document has no office:spreadsheet body element.");
            return new FodsWorksheetCollection(spreadsheet);
        }
    }
}
