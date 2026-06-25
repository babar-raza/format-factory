// FormatFactory.Ndjson — Typed record wrapper (QF-3-003, TC-QF-R-008)

using System.Collections.Generic;
using System.Linq;
using System.Text.Json;

namespace FormatFactory.Ndjson;

/// <summary>
/// A typed wrapper around a single parsed NDJSON record (JSON object).
/// Provides domain-specific field access over <see cref="System.Text.Json.JsonElement"/>.
/// </summary>
public sealed class NdjsonRecord
{
    private readonly JsonElement _element;

    /// <summary>Creates an <see cref="NdjsonRecord"/> wrapping the given JSON element.</summary>
    public NdjsonRecord(JsonElement element)
    {
        _element = element;
    }

    /// <summary>
    /// All top-level field name → <see cref="JsonElement"/> pairs in this record.
    /// Returns an empty dictionary for non-object records (arrays, primitives).
    /// </summary>
    public IReadOnlyDictionary<string, JsonElement> Fields =>
        _element.ValueKind == JsonValueKind.Object
            ? _element.EnumerateObject().ToDictionary(p => p.Name, p => p.Value)
            : new Dictionary<string, JsonElement>();

    /// <summary>All top-level field names in this record.</summary>
    public IReadOnlyList<string> Keys =>
        _element.ValueKind == JsonValueKind.Object
            ? _element.EnumerateObject().Select(p => p.Name).ToList()
            : new List<string>();

    /// <summary>
    /// Tries to get the <see cref="JsonElement"/> for the given field key.
    /// Returns false for non-object records or missing keys.
    /// </summary>
    public bool TryGetValue(string key, out JsonElement value)
    {
        if (_element.ValueKind == JsonValueKind.Object)
            return _element.TryGetProperty(key, out value);
        value = default;
        return false;
    }

    /// <summary>The underlying raw <see cref="JsonElement"/>.</summary>
    public JsonElement RawElement => _element;
}
