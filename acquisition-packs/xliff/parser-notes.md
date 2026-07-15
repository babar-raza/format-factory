# Parser Notes: XLIFF

## Parsing Strategy
- **Primary module:** xml.etree.ElementTree (stdlib)
- **Reuse pattern:** XML-based codec pattern (similar to FODT/FODP codecs)
- **Estimated LOC:** 300-400

## Detection (Probe)
Check for `.xliff` or `.xlf` extension. Validate by parsing as XML and checking for the `<xliff>` root element with the XLIFF 2.1 namespace (`urn:oasis:names:tc:xliff:document:2.0`).

## Loading
Parse the XML document using `xml.etree.ElementTree.parse()`. Navigate the tree to extract `<file>` elements, their `<unit>` children, and the `<segment>` / `<source>` / `<target>` text content. Handle inline elements (`<ph>`, `<pc>`, `<mrk>`) by preserving them in the model. Build a structured model of translation units.

## Writing
Construct the XML tree from the translation model using ElementTree, writing proper namespace declarations and inline markup. Write support planned.

## Dependencies
- stdlib only (xml.etree.ElementTree)
- No new external dependencies required
