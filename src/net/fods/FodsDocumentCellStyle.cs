// FormatFactory.Fods -- Cell-level style and formatting APIs (font, alignment, colors,
// wrapping, number format, background, text properties).
// Partial class extension for FodsDocument.

using System;
using System.Collections.Generic;
using System.Xml.Linq;

namespace FormatFactory.Fods;

public sealed partial class FodsDocument
{
    // -------------------------------------------------------------------------
    // Cell number format (R293, R330)
    // -------------------------------------------------------------------------

    private readonly Dictionary<(string Sheet, int Row, int Col), string> _cellNumberFormats = new();

    /// <summary>R293: Set a number format string on the specified cell.</summary>
    public void SetCellNumberFormat(string sheetName, int row, int col, string format)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        _cellNumberFormats[(sheetName, row, col)] = format ?? string.Empty;
    }

    /// <summary>R293: Get the number format string for the specified cell, or empty if none set.</summary>
    public string GetCellNumberFormat(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _cellNumberFormats.TryGetValue((sheetName, row, col), out var fmt) ? fmt : string.Empty;
    }

    // -------------------------------------------------------------------------
    // Cell alignment (R295, R348)
    // -------------------------------------------------------------------------

    private readonly Dictionary<(string Sheet, int Row, int Col), string> _cellAlignment = new();

    /// <summary>R295: Set cell horizontal alignment (left/center/right).</summary>
    public void SetCellAlignment(string sheetName, int row, int col, string alignment)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        _cellAlignment[(sheetName, row, col)] = alignment ?? string.Empty;
    }

    /// <summary>R348: Return the horizontal alignment set on the specified cell, or empty if not set.</summary>
    public string? GetCellAlignment(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _cellAlignment.TryGetValue((sheetName, row, col), out var align) ? align : string.Empty;
    }

    // -------------------------------------------------------------------------
    // Cell font (R297, R345)
    // -------------------------------------------------------------------------

    private readonly Dictionary<(string Sheet, int Row, int Col), (string Font, double Size, bool Bold)> _cellFont = new();

    /// <summary>R297: Set cell font (5-arg: name, size — bold defaults to false).</summary>
    public void SetCellFont(string sheetName, int row, int col, string fontName, double size)
        => SetCellFont(sheetName, row, col, fontName, size, false);

    /// <summary>R297: Set cell font (6-arg: name, size, bold).</summary>
    public void SetCellFont(string sheetName, int row, int col, string fontName, double size, bool bold)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        _cellFont[(sheetName, row, col)] = (fontName ?? string.Empty, size, bold);
    }

    /// <summary>R345: Set cell font by name only (4-arg: no size/bold).</summary>
    public void SetCellFont(string sheetName, int row, int col, string fontName)
        => SetCellFont(sheetName, row, col, fontName, 11.0);

    /// <summary>R345: Return the font name set on the specified cell, or empty if not set.</summary>
    public string? GetCellFont(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _cellFont.TryGetValue((sheetName, row, col), out var f) ? f.Font : string.Empty;
    }

    // -------------------------------------------------------------------------
    // Cell wrapping (R298, R373)
    // -------------------------------------------------------------------------

    private readonly Dictionary<(string Sheet, int Row, int Col), bool> _cellWrapping = new();

    /// <summary>R298: Set cell text wrapping.</summary>
    public void SetCellWrapping(string sheetName, int row, int col, bool wrap)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        _cellWrapping[(sheetName, row, col)] = wrap;
    }

    /// <summary>R373: Return cell wrap-text setting.</summary>
    public bool GetCellWrapText(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _cellWrapping.TryGetValue((sheetName, row, col), out var v) && v;
    }

    /// <summary>R373: Set cell wrap-text (alias for SetCellWrapping).</summary>
    public void SetCellWrapText(string sheetName, int row, int col, bool wrap)
        => SetCellWrapping(sheetName, row, col, wrap);

    // -------------------------------------------------------------------------
    // Cell background (R342)
    // -------------------------------------------------------------------------

    private readonly Dictionary<(string Sheet, int Row, int Col), string> _cellBackgrounds = new();

    /// <summary>R342: Get the background color string for the specified cell, or empty if none set.</summary>
    public string? GetCellBackground(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _cellBackgrounds.TryGetValue((sheetName, row, col), out var bg) ? bg : string.Empty;
    }

    // -------------------------------------------------------------------------
    // Cell font color (R350, R351, R384) — writes to ODF XML style
    // -------------------------------------------------------------------------

    private readonly Dictionary<(string Sheet, int Row, int Col), string> _cellFontColors = new();

    /// <summary>R350: Set the font color of the specified cell; writes to ODF XML style.</summary>
    public void SetCellFontColor(string sheetName, int row, int col, string color)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        color ??= string.Empty;
        _cellFontColors[(sheetName, row, col)] = color;
        var cellEl = GetCellElementDirect(sheetName, row, col);
        if (cellEl is not null && !string.IsNullOrEmpty(color))
            FodsStyleEditor.SetCellFontColor(_doc, cellEl, color);
    }

    /// <summary>R351: Get the font color of the specified cell via ODF style chain.
    /// In-memory override takes priority; falls back to style:text-properties/@fo:color.</summary>
    public string GetCellFontColor(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        if (_cellFontColors.TryGetValue((sheetName, row, col), out var ov)) return ov;
        var cellEl = GetCellElementDirect(sheetName, row, col);
        return cellEl is null ? string.Empty : (FodsStyleResolver.ResolveCellStyle(_doc, cellEl).FontColor ?? string.Empty);
    }

    /// <summary>R384: Return the text color of the cell (alias for GetCellFontColor).</summary>
    public string? GetCellTextColor(string sheetName, int row, int col)
        => GetCellFontColor(sheetName, row, col);

    /// <summary>R384: Set the text color of the cell (alias for SetCellFontColor).</summary>
    public void SetCellTextColor(string sheetName, int row, int col, string color)
        => SetCellFontColor(sheetName, row, col, color);

    // -------------------------------------------------------------------------
    // Cell font size instance overloads (R346)
    // -------------------------------------------------------------------------

    /// <summary>R346: Set the font size of the specified cell on the named sheet (int overload).</summary>
    public void SetCellFontSize(string sheetName, int row, int col, int size)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        SetCellFontSize(sheet, row, col, size);
    }

    // -------------------------------------------------------------------------
    // Cell style name (R357)
    // -------------------------------------------------------------------------

    /// <summary>R357: Return the style-name attribute of the cell, or empty string if none set.</summary>
    public string GetCellStyleName(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return GetCellStyle(sheetName, row, col) ?? string.Empty;
    }

    // -------------------------------------------------------------------------
    // Cell background color via XML (R382)
    // -------------------------------------------------------------------------

    /// <summary>R382: Return the background color of the cell from ODF XML.
    /// Returns "transparent" if no background color has been set.</summary>
    public string GetCellBackgroundColor(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new InvalidOperationException($"No sheet named '{sheetName}' exists.");
        var color = GetCellColor(sheetName, row, col);
        return color is { Length: > 0 } ? color : "transparent";
    }

    // -------------------------------------------------------------------------
    // Cell merge status (R383)
    // -------------------------------------------------------------------------

    /// <summary>R383: Return the merge status of the cell: "anchor", "covered", or "none".</summary>
    public string? GetCellMergeStatus(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        var sheet = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        if (row >= sheet.Rows.Count) return "none";
        var rowObj = sheet.Rows[row];
        if (col >= rowObj.Cells.Count) return "none";
        var cell = rowObj.Cells[col];
        var ns = XNamespace.Get("urn:oasis:names:tc:opendocument:xmlns:table:1.0");
        if (cell.Element.Attribute(ns + "number-columns-spanned") != null ||
            cell.Element.Attribute(ns + "number-rows-spanned") != null)
            return "anchor";
        if (cell.Element.Name.LocalName == "covered-table-cell")
            return "covered";
        return "none";
    }

    // -------------------------------------------------------------------------
    // Cell formula type (R394)
    // -------------------------------------------------------------------------

    /// <summary>R394: Return the formula type for the cell ("formula" if formula present, "none" otherwise).</summary>
    public string GetCellFormulaType(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        var formula = GetCellFormula(sheetName, row, col);
        return string.IsNullOrEmpty(formula) ? "none" : "formula";
    }

    // -------------------------------------------------------------------------
    // Cell font names (R377)
    // -------------------------------------------------------------------------

    private readonly Dictionary<(string Sheet, int Row, int Col), string> _cellFontNames = new();

    /// <summary>R377: Return the font name for the specified cell, or empty string if not set.</summary>
    public string? GetCellFontName(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _cellFontNames.TryGetValue((sheetName, row, col), out var n) ? n : string.Empty;
    }

    /// <summary>R377: Set the font name for the specified cell.</summary>
    public void SetCellFontName(string sheetName, int row, int col, string fontName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        _cellFontNames[(sheetName, row, col)] = fontName ?? string.Empty;
    }

    // -------------------------------------------------------------------------
    // Cell font size (R376)
    // -------------------------------------------------------------------------

    private readonly Dictionary<(string Sheet, int Row, int Col), double> _cellFontSizes = new();

    /// <summary>R376: Return the font size for the specified cell, or 10.0 if not set.</summary>
    public double GetCellFontSize(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _cellFontSizes.TryGetValue((sheetName, row, col), out var sz) ? sz : 10.0;
    }

    /// <summary>R376: Set the font size for the specified cell (double overload).</summary>
    public void SetCellFontSize(string sheetName, int row, int col, double size)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        _cellFontSizes[(sheetName, row, col)] = size;
    }

    // -------------------------------------------------------------------------
    // Cell font bold (R378)
    // -------------------------------------------------------------------------

    private readonly Dictionary<(string Sheet, int Row, int Col), bool> _cellFontBold = new();

    /// <summary>R378: Return whether the cell font is bold; false if not set.</summary>
    public bool GetCellFontBold(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _cellFontBold.TryGetValue((sheetName, row, col), out var b) && b;
    }

    /// <summary>R378: Set whether the cell font is bold.</summary>
    public void SetCellFontBold(string sheetName, int row, int col, bool bold)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        _cellFontBold[(sheetName, row, col)] = bold;
    }

    // -------------------------------------------------------------------------
    // Cell font italic (R379)
    // -------------------------------------------------------------------------

    private readonly Dictionary<(string Sheet, int Row, int Col), bool> _cellFontItalic = new();

    /// <summary>R379: Return whether the cell font is italic; false if not set.</summary>
    public bool GetCellFontItalic(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _cellFontItalic.TryGetValue((sheetName, row, col), out var i) && i;
    }

    /// <summary>R379: Set whether the cell font is italic.</summary>
    public void SetCellFontItalic(string sheetName, int row, int col, bool italic)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        _cellFontItalic[(sheetName, row, col)] = italic;
    }

    // -------------------------------------------------------------------------
    // Cell font underline (R380)
    // -------------------------------------------------------------------------

    private readonly Dictionary<(string Sheet, int Row, int Col), bool> _cellFontUnderline = new();

    /// <summary>R380: Return whether the cell font is underlined; false if not set.</summary>
    public bool GetCellFontUnderline(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _cellFontUnderline.TryGetValue((sheetName, row, col), out var u) && u;
    }

    /// <summary>R380: Set whether the cell font is underlined.</summary>
    public void SetCellFontUnderline(string sheetName, int row, int col, bool underline)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        _cellFontUnderline[(sheetName, row, col)] = underline;
    }

    // -------------------------------------------------------------------------
    // Cell font strikethrough (R381)
    // -------------------------------------------------------------------------

    private readonly Dictionary<(string Sheet, int Row, int Col), bool> _cellFontStrikethrough = new();

    /// <summary>R381: Return whether the cell font has strikethrough; false if not set.</summary>
    public bool GetCellFontStrikethrough(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _cellFontStrikethrough.TryGetValue((sheetName, row, col), out var s) && s;
    }

    /// <summary>R381: Set whether the cell font has strikethrough.</summary>
    public void SetCellFontStrikethrough(string sheetName, int row, int col, bool strikethrough)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        _cellFontStrikethrough[(sheetName, row, col)] = strikethrough;
    }

    // -------------------------------------------------------------------------
    // Cell text rotation (R388)
    // -------------------------------------------------------------------------

    private readonly Dictionary<(string Sheet, int Row, int Col), int> _cellTextRotation = new();

    /// <summary>R388: Return the text rotation angle (degrees) for the cell, or 0 if not set.</summary>
    public int GetCellTextRotation(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _cellTextRotation.TryGetValue((sheetName, row, col), out var r) ? r : 0;
    }

    /// <summary>R388: Set the text rotation angle (degrees) for the cell.</summary>
    public void SetCellTextRotation(string sheetName, int row, int col, int degrees)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        _cellTextRotation[(sheetName, row, col)] = degrees;
    }

    // -------------------------------------------------------------------------
    // Cell indent (R389)
    // -------------------------------------------------------------------------

    private readonly Dictionary<(string Sheet, int Row, int Col), int> _cellIndent = new();

    /// <summary>R389: Return the indent level for the cell, or 0 if not set.</summary>
    public int GetCellIndent(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _cellIndent.TryGetValue((sheetName, row, col), out var v) ? v : 0;
    }

    /// <summary>R389: Set the indent level for the cell.</summary>
    public void SetCellIndent(string sheetName, int row, int col, int indent)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        _cellIndent[(sheetName, row, col)] = indent;
    }

    // -------------------------------------------------------------------------
    // Cell vertical alignment (R390)
    // -------------------------------------------------------------------------

    private readonly Dictionary<(string Sheet, int Row, int Col), string> _cellVerticalAlign = new();

    /// <summary>R390: Return the vertical alignment for the cell ("bottom" if not set).</summary>
    public string GetCellVerticalAlign(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _cellVerticalAlign.TryGetValue((sheetName, row, col), out var v) ? v : "bottom";
    }

    /// <summary>R390: Set the vertical alignment for the cell.</summary>
    public void SetCellVerticalAlign(string sheetName, int row, int col, string align)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        _cellVerticalAlign[(sheetName, row, col)] = align ?? "bottom";
    }

    // -------------------------------------------------------------------------
    // Cell error value (R393)
    // -------------------------------------------------------------------------

    private readonly Dictionary<(string Sheet, int Row, int Col), string> _cellErrors = new();

    /// <summary>R393: Return the error string for the cell (empty string if no error).</summary>
    public string GetCellErrorValue(string sheetName, int row, int col)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        return _cellErrors.TryGetValue((sheetName, row, col), out var v) ? v : string.Empty;
    }

    /// <summary>R393: Set an error string for the cell.</summary>
    public void SetCellError(string sheetName, int row, int col, string error)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
            throw new ArgumentException("sheetName must not be null or whitespace.", nameof(sheetName));
        if (row < 0) throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0) throw new ArgumentOutOfRangeException(nameof(col));
        _ = GetSheetByName(sheetName)
            ?? throw new ArgumentException($"No sheet named '{sheetName}'.", nameof(sheetName));
        _cellErrors[(sheetName, row, col)] = error ?? string.Empty;
    }
}
