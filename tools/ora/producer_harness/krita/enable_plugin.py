"""Enable the ora_harness_driver PyKrita plugin in an isolated kritarc.

FIRST APPROACH (superseded, kept here as the empirical record): this
originally used PyQt5's own QSettings to write the [python]/enable_plugins
list, reasoning that Krita links against the same Qt serialization engine.
That reasoning was WRONG in a way only the real running application
revealed: Krita's own kritarc reader is KConfig (KDE Frameworks' own config
system, not plain Qt QSettings) -- confirmed directly from the real error
Krita itself printed on first run: `kf.config.core: "KConfigIni: In file
.../kritarc, line 2: " "Invalid escape sequence \"\\0\"."`, repeated for
every byte of QSettings' own binary `@Variant(...)` blob encoding, which
KConfigIni's own parser does not understand at all. Both are "ini-style"
formats but are NOT the same serialization engine, despite Krita itself
being built on top of Qt.

SECOND approach (also superseded): KConfig's own documented list encoding
is a plain comma-separated string (KConfigGroup::writeEntry(key,
QStringList)) -- this fixed the parse errors (KConfigIni read the file
without complaint) but Krita's own scripting log then reported the exact,
unambiguous root cause directly: `krita.scripting: Trying to load plugin
"ora_harness_driver" . Enabled: false . Broken: false` -- the plugin was
correctly discovered (module path resolved, .desktop parsed) but PyKrita's
own C++ plugin manager does not treat presence-in-a-shared-list as
"enabled" at all. `enable_plugins` is not the real per-plugin gate.

THIRD approach (also superseded): a per-plugin boolean key named exactly
after the module directory (`ora_harness_driver=true`) -- kritarc was
byte-for-byte confirmed correct and Krita's own KConfigIni parser accepted
it without complaint, yet the exact same `Enabled: false` log line
persisted. This ruled out "bare module name as key" definitively rather
than by assumption.

FOURTH (current) approach: rather than guess a 4th key shape, extracted the
literal config-key string directly from the compiled plugin binary itself
(`/usr/lib/x86_64-linux-gnu/kritaplugins/kritapykrita.so`) via a plain byte
scan for printable ASCII runs -- it contains exactly the literal `"enable_"`
(7 characters, nothing appended, confirmed by widening the scan and finding
no continuation), meaning PythonPluginManager.cpp builds the real key by
string concatenation: "enable_" + moduleName. Written directly here as
ground truth from the binary, not inferred from behavior.
"""
import sys

config_path = sys.argv[1]
plugin_name = sys.argv[2]

with open(config_path, "a", encoding="utf-8") as handle:
    handle.write("[python]\nenable_%s=true\n" % plugin_name)
print("wrote enable_%s=true to %s" % (plugin_name, config_path))
