# Parser Notes: MaterialX

## Parsing Strategy
- **Primary module:** xml.etree.ElementTree (stdlib)
- **Reuse pattern:** XML-based codec pattern (similar to FODT/FODP codecs)
- **Estimated LOC:** 300-400

## Detection (Probe)
Check for `.mtlx` extension. Validate by parsing as XML and checking for the `<materialx>` root element with a `version` attribute matching a known MaterialX version string.

## Loading
Parse the XML document using `xml.etree.ElementTree.parse()`. Extract node definitions (`<nodedef>`), node graphs (`<nodegraph>`), material assignments (`<surfacematerial>`), and typed inputs/outputs. Resolve inheritance chains through `inherit` attributes. Build a structured model of the material graph with typed connections.

## Writing
Construct the XML tree from the material model, writing proper element hierarchies for node graphs, shader references, and typed inputs. Write support planned.

## Dependencies
- stdlib only (xml.etree.ElementTree)
- No new external dependencies required
