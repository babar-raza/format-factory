// FormatFactory.Csv — .NET CSV analytics partial class
// Extracted from CsvDocument.cs per RULE-LIB-004 (<800 LOC per partial)

using System;
using System.Collections.Generic;
using System.Linq;

namespace FormatFactory.Csv;

/// <summary>Analytics extension partial for CsvDocument.</summary>
public sealed partial class CsvDocument
{
    private static IEnumerable<double> ParseNumericColumn(List<string> values) =>
        values
            .Where(v => double.TryParse(v, System.Globalization.NumberStyles.Any, System.Globalization.CultureInfo.InvariantCulture, out _))
            .Select(v => double.Parse(v, System.Globalization.CultureInfo.InvariantCulture));

    /// <summary>Returns the minimum numeric value in the specified column.</summary>
    public double GetColumnMin(int index) => ParseNumericColumn(GetColumn(index)).Min();

    /// <summary>Returns the maximum numeric value in the specified column.</summary>
    public double GetColumnMax(int index) => ParseNumericColumn(GetColumn(index)).Max();

    /// <summary>Returns the sum of numeric values in the specified column (by index).</summary>
    public double GetColumnSum(int index) => ParseNumericColumn(GetColumn(index)).Sum();

    /// <summary>Returns the sum of numeric values in the specified column (by header name).</summary>
    public double GetColumnSum(string headerName) => ParseNumericColumn(GetColumn(headerName)).Sum();

    /// <summary>Returns the arithmetic mean of numeric values in the specified column.</summary>
    public double GetColumnMean(int index) => ParseNumericColumn(GetColumn(index)).Average();

    /// <summary>Returns the range (max minus min) of numeric values in the specified column (by index).</summary>
    public double GetColumnRange(int index) => GetColumnMax(index) - GetColumnMin(index);

    /// <summary>Returns the range (max minus min) of numeric values in the specified column (by header name).</summary>
    public double GetColumnRange(string headerName) => GetColumnMax(headerName) - GetColumnMin(headerName);

    /// <summary>Returns the minimum numeric value in the specified column (by header name).</summary>
    public double GetColumnMin(string headerName) => ParseNumericColumn(GetColumn(headerName)).Min();

    /// <summary>Returns the maximum numeric value in the specified column (by header name).</summary>
    public double GetColumnMax(string headerName) => ParseNumericColumn(GetColumn(headerName)).Max();

    /// <summary>Returns the arithmetic mean of numeric values in the specified column (by header name).</summary>
    public double GetColumnMean(string headerName) => ParseNumericColumn(GetColumn(headerName)).Average();

    /// <summary>Returns the median of numeric values in the specified column.</summary>
    public double GetColumnMedian(int index) => _Median(ParseNumericColumn(GetColumn(index)).OrderBy(x => x).ToArray());

    /// <summary>Returns the median of numeric values in the specified column (by header name).</summary>
    public double GetColumnMedian(string headerName) => _Median(ParseNumericColumn(GetColumn(headerName)).OrderBy(x => x).ToArray());

    private static double _Median(double[] sorted)
    {
        if (sorted.Length == 0) throw new InvalidOperationException("Column has no numeric values.");
        int mid = sorted.Length / 2;
        return sorted.Length % 2 == 1 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2.0;
    }

    /// <summary>Returns the most frequently occurring string value in the specified column.</summary>
    public string GetColumnMode(int index) => _ModeString(GetColumn(index));

    /// <summary>Returns the most frequently occurring string value in the specified column (by header name).</summary>
    public string GetColumnMode(string headerName) => _ModeString(GetColumn(headerName));

    private static string _ModeString(IEnumerable<string> values)
    {
        var grp = values.GroupBy(v => v).OrderByDescending(g => g.Count()).FirstOrDefault();
        if (grp == null) throw new InvalidOperationException("Column has no values.");
        return grp.Key;
    }

    /// <summary>Returns the population variance of numeric values in the specified column.</summary>
    public double GetColumnVariance(int index) => _Variance(ParseNumericColumn(GetColumn(index)).ToArray());

    /// <summary>Returns the population variance of numeric values in the specified column (by header name).</summary>
    public double GetColumnVariance(string headerName) => _Variance(ParseNumericColumn(GetColumn(headerName)).ToArray());

    private static double _Variance(double[] vals)
    {
        if (vals.Length == 0) throw new InvalidOperationException("Column has no numeric values.");
        double mean = vals.Average();
        return vals.Average(v => (v - mean) * (v - mean));
    }

    /// <summary>Returns the population standard deviation of numeric values in the specified column.</summary>
    public double GetColumnStdDev(int index) => Math.Sqrt(GetColumnVariance(index));

    /// <summary>Returns the population standard deviation of numeric values in the specified column (by header name).</summary>
    public double GetColumnStdDev(string headerName) => Math.Sqrt(GetColumnVariance(headerName));

    /// <summary>Returns the first quartile (Q1) of numeric values in the specified column.</summary>
    public double GetColumnFirstQuartile(int index) => _Quartile(ParseNumericColumn(GetColumn(index)).OrderBy(x => x).ToArray(), 0.25);

    /// <summary>Returns the first quartile (Q1) of numeric values in the specified column (by header name).</summary>
    public double GetColumnFirstQuartile(string headerName) => _Quartile(ParseNumericColumn(GetColumn(headerName)).OrderBy(x => x).ToArray(), 0.25);

    /// <summary>Returns the third quartile (Q3) of numeric values in the specified column.</summary>
    public double GetColumnThirdQuartile(int index) => _Quartile(ParseNumericColumn(GetColumn(index)).OrderBy(x => x).ToArray(), 0.75);

    /// <summary>Returns the third quartile (Q3) of numeric values in the specified column (by header name).</summary>
    public double GetColumnThirdQuartile(string headerName) => _Quartile(ParseNumericColumn(GetColumn(headerName)).OrderBy(x => x).ToArray(), 0.75);

    private static double _Quartile(double[] sorted, double q)
    {
        if (sorted.Length == 0) throw new InvalidOperationException("Column has no numeric values.");
        double idx = q * (sorted.Length - 1);
        int lo = (int)Math.Floor(idx);
        int hi = (int)Math.Ceiling(idx);
        return lo == hi ? sorted[lo] : sorted[lo] + (sorted[hi] - sorted[lo]) * (idx - lo);
    }

    /// <summary>Returns the interquartile range (Q3 - Q1) of numeric values in the specified column.</summary>
    public double GetColumnInterquartileRange(int index)
    {
        var sorted = ParseNumericColumn(GetColumn(index)).OrderBy(x => x).ToArray();
        if (sorted.Length == 0) throw new InvalidOperationException("Column has no numeric values.");
        return _Quartile(sorted, 0.75) - _Quartile(sorted, 0.25);
    }
    /// <summary>Returns the interquartile range (Q3 - Q1) of numeric values in the named column.</summary>
    public double GetColumnInterquartileRange(string headerName) => GetColumnInterquartileRange(GetColumnIndex(headerName));

    /// <summary>Returns the number of distinct values in the specified column.</summary>
    public int GetColumnUniqueCount(int index) => GetColumn(index).Distinct().Count();

    /// <summary>Returns the number of distinct values in the specified column (by header name).</summary>
    public int GetColumnUniqueCount(string headerName) => GetColumn(headerName).Distinct().Count();

    /// <summary>Returns the cardinality (distinct count) of the specified column.</summary>
    public int GetColumnCardinality(int index) => GetColumnUniqueCount(index);

    /// <summary>Returns the cardinality (distinct count) of the specified column (by header name).</summary>
    public int GetColumnCardinality(string headerName) => GetColumnUniqueCount(headerName);

    /// <summary>Returns the Shannon entropy of values in the specified column.</summary>
    public double GetColumnEntropy(int index) => _Entropy(GetColumn(index));

    /// <summary>Returns the Shannon entropy of values in the specified column (by header name).</summary>
    public double GetColumnEntropy(string headerName) => _Entropy(GetColumn(headerName));

    private static double _Entropy(List<string> values)
    {
        if (values.Count == 0) return 0.0;
        var counts = values.GroupBy(v => v).Select(g => (double)g.Count() / values.Count);
        return -counts.Sum(p => p > 0 ? p * Math.Log(p, 2) : 0.0);
    }

    /// <summary>Returns the Fisher skewness of numeric values in the specified column.</summary>
    public double GetColumnSkewness(int index) => _Skewness(ParseNumericColumn(GetColumn(index)).ToArray());

    /// <summary>Returns the Fisher skewness of numeric values in the specified column (by header name).</summary>
    public double GetColumnSkewness(string headerName) => _Skewness(ParseNumericColumn(GetColumn(headerName)).ToArray());

    private static double _Skewness(double[] vals)
    {
        if (vals.Length < 2) return 0.0;
        double mean = vals.Average();
        double std = Math.Sqrt(vals.Average(v => (v - mean) * (v - mean)));
        if (std == 0) return 0.0;
        return vals.Average(v => Math.Pow((v - mean) / std, 3));
    }

    /// <summary>Returns the excess kurtosis of numeric values in the specified column.</summary>
    public double GetColumnKurtosis(int index) => _Kurtosis(ParseNumericColumn(GetColumn(index)).ToArray());

    /// <summary>Returns the excess kurtosis of numeric values in the specified column (by header name).</summary>
    public double GetColumnKurtosis(string headerName) => _Kurtosis(ParseNumericColumn(GetColumn(headerName)).ToArray());

    private static double _Kurtosis(double[] vals)
    {
        if (vals.Length < 2) return 0.0;
        double mean = vals.Average();
        double std = Math.Sqrt(vals.Average(v => (v - mean) * (v - mean)));
        if (std == 0) return 0.0;
        return vals.Average(v => Math.Pow((v - mean) / std, 4)) - 3.0;
    }

    /// <summary>Returns the Z-score of a given value relative to the column distribution.</summary>
    public double GetColumnZScore(int index, double value)
    {
        var vals = ParseNumericColumn(GetColumn(index)).ToArray();
        if (vals.Length == 0) throw new InvalidOperationException("Column has no numeric values.");
        double mean = vals.Average();
        double std = Math.Sqrt(vals.Average(v => (v - mean) * (v - mean)));
        return std == 0 ? 0.0 : (value - mean) / std;
    }

    /// <summary>Returns the Z-score of a given value relative to the column distribution (by header name).</summary>
    public double GetColumnZScore(string headerName, double value)
    {
        var vals = ParseNumericColumn(GetColumn(headerName)).ToArray();
        if (vals.Length == 0) throw new InvalidOperationException("Column has no numeric values.");
        double mean = vals.Average();
        double std = Math.Sqrt(vals.Average(v => (v - mean) * (v - mean)));
        return std == 0 ? 0.0 : (value - mean) / std;
    }

    /// <summary>Returns the Z-score of the value at the given row index in the named column.</summary>
    public double GetColumnZScore(string headerName, int rowIndex)
    {
        var col = GetColumn(headerName);
        var vals = ParseNumericColumn(col).ToArray();
        if (vals.Length == 0) throw new InvalidOperationException("Column has no numeric values.");
        if (rowIndex < 0 || rowIndex >= col.Count) throw new ArgumentOutOfRangeException(nameof(rowIndex));
        double mean = vals.Average();
        double std = Math.Sqrt(vals.Average(v => (v - mean) * (v - mean)));
        if (!double.TryParse(col[rowIndex], System.Globalization.NumberStyles.Any, System.Globalization.CultureInfo.InvariantCulture, out double rowValue))
            return 0.0;
        return std == 0 ? 0.0 : (rowValue - mean) / std;
    }

    /// <summary>Returns the count of numeric values in the column whose |z-score| exceeds the threshold.</summary>
    public int GetColumnOutlierCount(int index, double threshold)
    {
        var vals = ParseNumericColumn(GetColumn(index)).ToArray();
        if (vals.Length == 0) return 0;
        double mean = vals.Average();
        double std = Math.Sqrt(vals.Average(v => (v - mean) * (v - mean)));
        if (std == 0) return 0;
        return vals.Count(v => Math.Abs((v - mean) / std) > threshold);
    }

    /// <summary>Returns the count of numeric values in the column whose |z-score| exceeds the threshold (by header name).</summary>
    public int GetColumnOutlierCount(string headerName, double threshold = 3.0)
    {
        var vals = ParseNumericColumn(GetColumn(headerName)).ToArray();
        if (vals.Length == 0) return 0;
        double mean = vals.Average();
        double std = Math.Sqrt(vals.Average(v => (v - mean) * (v - mean)));
        if (std == 0) return 0;
        return vals.Count(v => Math.Abs((v - mean) / std) > threshold);
    }

    // ── Additional statistical and utility methods ──────────────────────────────

    /// <summary>Returns the fraction of rows with missing (null or empty) values in the column.</summary>
    public double GetColumnMissingRate(string headerName) { var c = GetColumn(headerName); return c.Count == 0 ? 0.0 : (double)c.Count(v => string.IsNullOrEmpty(v)) / c.Count; }
    /// <summary>Returns the fraction of rows with non-missing values in the column (1 - missing rate).</summary>
    public double GetColumnFillRate(string headerName) => 1.0 - GetColumnMissingRate(headerName);
    /// <summary>Returns the fraction of distinct values in the column relative to the total row count.</summary>
    public double GetColumnDistinctRatio(string headerName) { var c = GetColumn(headerName); return c.Count == 0 ? 0.0 : (double)c.Distinct().Count() / c.Count; }
    /// <summary>Returns a dictionary mapping each distinct value to its occurrence count in the column.</summary>
    public Dictionary<string, int> GetColumnValueCounts(string headerName) => GetColumn(headerName).GroupBy(v => v).ToDictionary(g => g.Key, g => g.Count());
    /// <summary>Returns the most frequently occurring string value in the column.</summary>
    public string GetColumnTopValue(string headerName) => _ModeString(GetColumn(headerName));
    /// <summary>Returns the count of occurrences of the most frequent value in the column.</summary>
    public int GetColumnModeCount(string headerName) { var c = GetColumn(headerName); if (!c.Any()) return 0; return c.GroupBy(v => v).Max(g => g.Count()); }
    /// <summary>Returns the unique-value ratio (distinct count / row count) for the column.</summary>
    public double GetColumnUniqueRatio(string headerName) => GetColumnDistinctRatio(headerName);
    /// <summary>Returns the count of null or empty values in the column.</summary>
    public int GetNullCount(string headerName) => GetColumn(headerName).Count(v => string.IsNullOrEmpty(v));
    /// <summary>Returns the fill rate of the column (non-null fraction).</summary>
    public double GetFillRate(string headerName) => GetColumnFillRate(headerName);
    /// <summary>Returns the overall completeness of the document (fraction of non-empty cells).</summary>
    public double GetCompleteness() { if (RowCount == 0 || ColumnCount == 0) return 1.0; long total = (long)RowCount * ColumnCount; long filled = Rows.Sum(r => r.Count(v => !string.IsNullOrEmpty(v))); return (double)filled / total; }
    /// <summary>Returns the coefficient of variation (std / mean) for numeric values in the column.</summary>
    public double GetColumnCoefficientOfVariation(string headerName) { double m = GetColumnMean(headerName); return m == 0 ? 0.0 : GetColumnStdDev(headerName) / Math.Abs(m); }
    /// <summary>Returns the coefficient of variation alias.</summary>
    public double GetVarianceCoefficient(string col) => GetColumnCoefficientOfVariation(col);
    /// <summary>Returns the trimmed mean for the column, dropping the given fraction at each end.</summary>
    public double GetColumnTrimmedMean(string headerName, double fraction = 0.1) { if (fraction > 1.0) fraction /= 100.0; var s = ParseNumericColumn(GetColumn(headerName)).OrderBy(v => v).ToList(); if (s.Count == 0) return double.NaN; int trim = (int)(s.Count * fraction); var trimmed = s.Skip(trim).Take(Math.Max(1, s.Count - 2 * trim)).ToArray(); return trimmed.Average(); }
    /// <summary>Returns the trimmed mean alias.</summary>
    public double GetTrimmedMean(string col, double fraction = 0.1) => GetColumnTrimmedMean(col, fraction);
    /// <summary>Returns the Winsorized mean, replacing extreme values with the given percentile values.</summary>
    public double GetColumnWinsorizedMean(string headerName, double fraction = 0.1) { var s = ParseNumericColumn(GetColumn(headerName)).OrderBy(v => v).ToArray(); if (s.Length == 0) return double.NaN; int trim = (int)(s.Length * fraction); double lo = s[trim]; double hi = s[s.Length - 1 - trim]; return s.Select(v => Math.Max(lo, Math.Min(hi, v))).Average(); }
    /// <summary>Returns the normalized entropy (0 to 1) for the column.</summary>
    public double GetColumnEntropyNormalized(string headerName) { double e = GetColumnEntropy(headerName); int n = GetColumnUniqueCount(headerName); return n <= 1 ? 0.0 : e / Math.Log(n, 2); }
    /// <summary>Returns the normalized entropy alias.</summary>
    public double GetColumnNormalizedEntropy(string headerName) => GetColumnEntropyNormalized(headerName);
    /// <summary>Returns the information content (entropy in bits).
    /// Information content equals entropy in bits — same unit as GetColumnEntropy().
    /// The historical / Math.Log(2) divisor incorrectly converted bits to nats; removed.
    /// </summary>
    public double GetColumnInformationContent(string headerName) => GetColumnEntropy(headerName);
    /// <summary>Returns the diversity index (normalized entropy) for the column.</summary>
    public double GetColumnDiversity(string headerName) { int n = RowCount; if (n == 0) return 0.0; return (double)GetColumnUniqueCount(headerName) / n; }
    /// <summary>Returns the uniformity score (1 when all values equal, 0 when maximally diverse).</summary>
    public double GetColumnUniformity(string headerName) => 1.0 - GetColumnEntropyNormalized(headerName);
    /// <summary>Returns the mean absolute deviation of numeric values in the column.</summary>
    public double GetColumnMeanAbsoluteDeviation(string headerName) { var v = ParseNumericColumn(GetColumn(headerName)).ToArray(); if (v.Length == 0) return double.NaN; double m = v.Average(); return v.Average(x => Math.Abs(x - m)); }
    /// <summary>Returns the relative range (range / mean) for numeric values in the column.</summary>
    public double GetColumnRelativeRange(string headerName) { double m = GetColumnMean(headerName); return m == 0 ? 0.0 : GetColumnRange(headerName) / Math.Abs(m); }
    /// <summary>Returns the statistical moment of the given order for numeric values in the column.</summary>
    public double GetColumnMoment(string headerName, int order) { var v = ParseNumericColumn(GetColumn(headerName)).ToArray(); if (v.Length == 0) return double.NaN; double m = v.Average(); return v.Average(x => Math.Pow(x - m, order)); }
    /// <summary>Returns the Gini impurity for categorical values in the column.</summary>
    public double GetColumnGiniImpurity(string headerName) { var c = GetColumn(headerName); if (c.Count == 0) return 0.0; return 1.0 - c.GroupBy(v => v).Sum(g => Math.Pow((double)g.Count() / c.Count, 2)); }
    /// <summary>Returns the Gini coefficient for numeric values in the column.</summary>
    public double GetColumnGiniCoefficient(string headerName) { var v = ParseNumericColumn(GetColumn(headerName)).OrderBy(x => x).ToArray(); if (v.Length == 0) return 0.0; double sumAbs = 0; for (int i = 0; i < v.Length; i++) for (int j = 0; j < v.Length; j++) sumAbs += Math.Abs(v[i] - v[j]); return sumAbs / (2.0 * v.Length * v.Length * v.Average()); }
    /// <summary>Returns the Theil index (entropy-based inequality measure) for numeric values.</summary>
    public double GetColumnTheilIndex(string headerName) { var v = ParseNumericColumn(GetColumn(headerName)).Where(x => x > 0).ToArray(); if (v.Length == 0) return 0.0; double m = v.Average(); return v.Average(x => (x / m) * Math.Log(x / m)); }
    /// <summary>Returns the Pearson correlation between two numeric columns.</summary>
    public double GetColumnCorrelation(string col1, string col2) { var x = ParseNumericColumn(GetColumn(col1)).ToArray(); var y = ParseNumericColumn(GetColumn(col2)).ToArray(); int n = Math.Min(x.Length, y.Length); if (n == 0) return 0.0; double mx = x.Take(n).Average(), my = y.Take(n).Average(); double num = x.Take(n).Zip(y.Take(n), (a, b) => (a - mx) * (b - my)).Sum(); double dx = Math.Sqrt(x.Take(n).Sum(a => (a - mx) * (a - mx))); double dy = Math.Sqrt(y.Take(n).Sum(b => (b - my) * (b - my))); return (dx == 0 || dy == 0) ? 0.0 : num / (dx * dy); }
    /// <summary>Returns the correlation alias.</summary>
    public double GetCorrelation(string col1, string col2) => GetColumnCorrelation(col1, col2);
    /// <summary>Returns the covariance between two numeric columns.</summary>
    public double GetColumnCovariance(string col1, string col2) { var x = ParseNumericColumn(GetColumn(col1)).ToArray(); var y = ParseNumericColumn(GetColumn(col2)).ToArray(); int n = Math.Min(x.Length, y.Length); if (n == 0) return 0.0; double mx = x.Take(n).Average(), my = y.Take(n).Average(); return x.Take(n).Zip(y.Take(n), (a, b) => (a - mx) * (b - my)).Sum() / n; }
    /// <summary>Returns the covariance alias.</summary>
    public double GetCovariance(string col1, string col2) => GetColumnCovariance(col1, col2);
    /// <summary>Returns the mutual information between two columns.</summary>
    public double GetColumnMutualInformation(string col1, string col2) { var c1 = GetColumn(col1); var c2 = GetColumn(col2); int n = Math.Min(c1.Count, c2.Count); if (n == 0) return 0.0; var pairs = c1.Take(n).Zip(c2.Take(n), (a, b) => (a, b)).ToList(); double mi = 0; foreach (var g in pairs.GroupBy(p => p)) { double pxy = (double)g.Count() / n; double px = (double)c1.Take(n).Count(v => v == g.Key.a) / n; double py = (double)c2.Take(n).Count(v => v == g.Key.b) / n; if (px > 0 && py > 0 && pxy > 0) mi += pxy * Math.Log(pxy / (px * py)); } return mi; }
    /// <summary>Returns the mutual information alias.</summary>
    public double GetMutualInformation(string col1, string col2) => GetColumnMutualInformation(col1, col2);
    /// <summary>Returns the auto-correlation of numeric values in the column at the given lag.</summary>
    public double GetColumnAutoCorrelation(string headerName, int lag = 1) { var v = ParseNumericColumn(GetColumn(headerName)).ToArray(); int n = v.Length - lag; if (n <= 0) return 0.0; double m = v.Average(); double var = v.Sum(x => (x - m) * (x - m)); if (var == 0) return 0.0; return v.Take(n).Zip(v.Skip(lag), (a, b) => (a - m) * (b - m)).Sum() / var; }
    /// <summary>Returns the partial correlation between col1 and col2 (approximated as first-order bivariate).</summary>
    public double GetColumnPartialCorrelation(string col1, string col2) { return GetColumnCorrelation(col1, col2); }
    /// <summary>Returns the partial correlation between col1 and col2 controlling for controlCol (first-order partial).</summary>
    public double GetColumnPartialCorrelation(string col1, string col2, string controlCol) { double rxy = GetColumnCorrelation(col1, col2); double rxz = GetColumnCorrelation(col1, controlCol); double ryz = GetColumnCorrelation(col2, controlCol); double denom = Math.Sqrt((1 - rxz * rxz) * (1 - ryz * ryz)); if (denom == 0) return 0.0; return (rxy - rxz * ryz) / denom; }
    /// <summary>Returns the linear regression slope (col2 ~ col1).</summary>
    public double GetLinearRegressionSlope(string col1, string col2) { var x = ParseNumericColumn(GetColumn(col1)).ToArray(); var y = ParseNumericColumn(GetColumn(col2)).ToArray(); int n = Math.Min(x.Length, y.Length); if (n == 0) return 0.0; double mx = x.Take(n).Average(), my = y.Take(n).Average(); double num = x.Take(n).Zip(y.Take(n), (a, b) => (a - mx) * (b - my)).Sum(); double den = x.Take(n).Sum(a => (a - mx) * (a - mx)); return den == 0 ? 0.0 : num / den; }
    /// <summary>Returns the linear regression intercept (col2 ~ col1).</summary>
    public double GetLinearRegressionIntercept(string col1, string col2) { var x = ParseNumericColumn(GetColumn(col1)).ToArray(); var y = ParseNumericColumn(GetColumn(col2)).ToArray(); int n = Math.Min(x.Length, y.Length); if (n == 0) return 0.0; return y.Take(n).Average() - GetLinearRegressionSlope(col1, col2) * x.Take(n).Average(); }
    /// <summary>Returns a predicted value from the linear regression model.</summary>
    public double GetPredictedValue(string col1, string col2, double x) => GetLinearRegressionSlope(col1, col2) * x + GetLinearRegressionIntercept(col1, col2);
    /// <summary>Returns the R² coefficient of determination for the linear regression.</summary>
    public double GetRSquared(string col1, string col2) { var r = GetColumnCorrelation(col1, col2); return r * r; }
    /// <summary>Returns the residual standard deviation for the linear regression.</summary>
    public double GetResidualStdDev(string col1, string col2) { var x = ParseNumericColumn(GetColumn(col1)).ToArray(); var y = ParseNumericColumn(GetColumn(col2)).ToArray(); int n = Math.Min(x.Length, y.Length); if (n < 2) return 0.0; double sl = GetLinearRegressionSlope(col1, col2), ic = GetLinearRegressionIntercept(col1, col2); double sse = x.Take(n).Zip(y.Take(n), (a, b) => Math.Pow(b - (sl * a + ic), 2)).Sum(); return Math.Sqrt(sse / Math.Max(1, n - 2)); }
    /// <summary>Returns the mean absolute error between two numeric columns.</summary>
    public double GetMeanAbsoluteError(string col1, string col2) { var x = ParseNumericColumn(GetColumn(col1)).ToArray(); var y = ParseNumericColumn(GetColumn(col2)).ToArray(); int n = Math.Min(x.Length, y.Length); if (n == 0) return 0.0; return x.Take(n).Zip(y.Take(n), (a, b) => Math.Abs(a - b)).Average(); }
    /// <summary>Returns the percentile value (0–100) for numeric values in the column.</summary>
    public double GetColumnPercentile(string headerName, double percentile) { var s = ParseNumericColumn(GetColumn(headerName)).OrderBy(v => v).ToArray(); if (s.Length == 0) return double.NaN; return _Quartile(s, percentile / 100.0); }
    /// <summary>Returns the percentile alias.</summary>
    public double GetPercentile(string col, double percentile) => GetColumnPercentile(col, percentile);
    /// <summary>Returns the quantile value (0–1 scale).</summary>
    public double GetColumnQuantile(string headerName, double q) => GetColumnPercentile(headerName, q * 100.0);
    /// <summary>Returns the percentile rank of a value within the column.</summary>
    public double GetColumnPercentileRank(string headerName, double value) { var v = ParseNumericColumn(GetColumn(headerName)).ToArray(); if (v.Length == 0) return 0.0; return 100.0 * v.Count(x => x <= value) / v.Length; }
    /// <summary>Returns the percentile rank alias.</summary>
    public double GetPercentileRank(string col, double value) => GetColumnPercentileRank(col, value);
    /// <summary>Returns the value at the d-th decile (d in 1–10) of the column.</summary>
    public double GetColumnDecile(string headerName, double d) => GetColumnPercentile(headerName, d * 10.0);
    /// <summary>Returns the rank of a value within the sorted column (1-based, rank 1 = highest).</summary>
    public int GetColumnRank(string headerName, double value) { var s = ParseNumericColumn(GetColumn(headerName)).OrderByDescending(v => v).ToList(); return s.TakeWhile(v => v > value).Count() + 1; }
    /// <summary>Returns the ordinal ranks of all numeric values in the column.</summary>
    public int[] GetColumnRankTransform(string headerName) { var v = ParseNumericColumn(GetColumn(headerName)).ToArray(); var sorted = v.OrderBy(x => x).ToList(); return v.Select(x => sorted.IndexOf(x) + 1).ToArray(); }
    /// <summary>Returns the IQR alias (interquartile range).</summary>
    public double GetColumnIQR(string headerName) => GetColumnThirdQuartile(headerName) - GetColumnFirstQuartile(headerName);
    /// <summary>Returns the IQR alias (non-column prefix).</summary>
    public double GetIQR(string col) => GetColumnThirdQuartile(col) - GetColumnFirstQuartile(col);
    /// <summary>Returns the cumulative sum of numeric values in the column.</summary>
    public double[] GetColumnCumulativeSum(string headerName) { var v = ParseNumericColumn(GetColumn(headerName)).ToList(); var res = new double[v.Count]; double acc = 0; for (int i = 0; i < v.Count; i++) { acc += v[i]; res[i] = acc; } return res; }
    /// <summary>Returns the cumulative sum alias.</summary>
    public double[] GetCumulativeSum(string col) => GetColumnCumulativeSum(col);
    /// <summary>Returns the moving average of numeric values in the column.</summary>
    public List<double> GetMovingAverage(string col, int window) { var v = ParseNumericColumn(GetColumn(col)).ToArray(); var res = new List<double>(); for (int i = 0; i < v.Length; i++) { int start = Math.Max(0, i - window + 1); res.Add(v.Skip(start).Take(i - start + 1).Average()); } return res; }
    /// <summary>Returns the running mean of numeric values in the column.</summary>
    public double[] GetColumnRunningMean(string headerName) => GetMovingAverage(headerName, 1).Select((_, i) => { var s = ParseNumericColumn(GetColumn(headerName)).Take(i + 1).ToArray(); return s.Average(); }).ToArray();
    /// <summary>Returns the z-score of a value in the column (non-column-prefixed alias).</summary>
    public double GetZScore(string col, double value) => GetColumnZScore(col, value);
    /// <summary>Returns the z-score for the value at a given row index in the column.</summary>
    public double GetZScore(string col, int rowIndex) { var vals = ParseNumericColumn(GetColumn(col)).ToArray(); if (vals.Length == 0 || rowIndex < 0 || rowIndex >= vals.Length) return double.NaN; double m = vals.Average(); double s = Math.Sqrt(vals.Average(v => (v - m) * (v - m))); return s == 0 ? 0.0 : (vals[rowIndex] - m) / s; }
    /// <summary>Returns z-scores for all numeric values in the column.</summary>
    public double[] GetZScores(string col) { var vals = ParseNumericColumn(GetColumn(col)).ToArray(); if (vals.Length == 0) return Array.Empty<double>(); double m = vals.Average(); double s = Math.Sqrt(vals.Average(v => (v - m) * (v - m))); return vals.Select(v => s == 0 ? 0.0 : (v - m) / s).ToArray(); }
    /// <summary>Returns the standardized (z-score) values for the column.</summary>
    public double[] GetColumnStandardizedValues(string headerName) => GetZScores(headerName);
    /// <summary>Returns the normalized (0–1 range) values for the column.</summary>
    public double[] GetColumnNormalizedValues(string headerName) { var v = ParseNumericColumn(GetColumn(headerName)).ToArray(); if (v.Length == 0) return Array.Empty<double>(); double mn = v.Min(), mx = v.Max(), r = mx - mn; return v.Select(x => r == 0 ? 0.0 : (x - mn) / r).ToArray(); }
    /// <summary>Returns normalized values alias.</summary>
    public List<double> GetColumnNormalized(string headerName) => GetColumnNormalizedValues(headerName).ToList();
    /// <summary>Returns normalized column alias (non-column-prefix).</summary>
    public List<double> GetNormalizedColumn(string col) => GetColumnNormalizedValues(col).ToList();
    /// <summary>Returns the robust scaled (median ± IQR) values for the column.</summary>
    public double[] GetColumnRobustScaledValues(string headerName) { var v = ParseNumericColumn(GetColumn(headerName)).ToArray(); if (v.Length == 0) return Array.Empty<double>(); double med = _Median(v.OrderBy(x => x).ToArray()); double iqr = GetColumnThirdQuartile(headerName) - GetColumnFirstQuartile(headerName); return v.Select(x => iqr == 0 ? 0.0 : (x - med) / iqr).ToArray(); }
    /// <summary>Returns the normality score (simple heuristic: |skewness| + |kurtosis - 3| normalized to 0–1).</summary>
    public double GetNormalityScore(string col) { try { double sk = Math.Abs(GetColumnSkewness(col)); double ku = Math.Abs(GetColumnKurtosis(col) - 3); return Math.Max(0, 1.0 - (sk + ku) / 10.0); } catch { return 0.5; } }
    /// <summary>Returns the outlier values (|z-score| > threshold) as a list.</summary>
    public List<double> GetColumnOutliers(string headerName, double threshold = 3.0) { var vals = ParseNumericColumn(GetColumn(headerName)).ToArray(); if (vals.Length == 0) return new List<double>(); double m = vals.Average(); double s = Math.Sqrt(vals.Average(v => (v - m) * (v - m))); return s == 0 ? new List<double>() : vals.Where(v => Math.Abs((v - m) / s) > threshold).ToList(); }
    /// <summary>Returns the outlier values alias.</summary>
    public List<double> GetOutliers(string col, double threshold = 3.0) => GetColumnOutliers(col, threshold);
    /// <summary>Returns the outlier count alias (non-column-prefix).</summary>
    public int GetOutlierCount(string col, double threshold = 3.0) => GetColumnOutlierCount(col, threshold);
    /// <summary>Returns distinct string values in the column.</summary>
    public List<string> GetDistinctValues(string headerName) => GetColumn(headerName).Distinct().ToList();
    /// <summary>Returns unique string values in the column.</summary>
    public List<string> GetUniqueValues(string headerName) => GetDistinctValues(headerName);
    /// <summary>Returns the count of unique values alias.</summary>
    public int GetUniqueValueCount(string headerName) => GetColumnUniqueCount(headerName);
    /// <summary>Returns the column values as a list (alias for GetColumn(string)).</summary>
    public List<string> GetColumnValues(string headerName) => GetColumn(headerName);
    /// <summary>Returns the column names (alias for Headers array as list).</summary>
    public List<string> GetColumnNames() => Headers?.ToList() ?? new List<string>();
    /// <summary>Returns column names as list.</summary>
    public List<string> GetHeaders() => Headers?.ToList() ?? new List<string>();
    /// <summary>Returns the number of headers (alias for ColumnCount).</summary>
    public int GetHeaderCount() => ColumnCount;
    /// <summary>Returns the row at the given index as a list of cell values. Index -1 returns the header row.</summary>
    public List<string> GetRow(int index)
    {
        if (index == -1) return Headers?.ToList() ?? new List<string>();
        return Rows[index].ToList();
    }
    /// <summary>Returns the row at the given index (alias for GetRow).</summary>
    public string[] GetRowAt(int index) => Rows[index];
    /// <summary>Returns the row values as a list.</summary>
    public List<string> GetRowValues(int index) => GetRow(index).ToList();
    /// <summary>Returns row count alias.</summary>
    public int GetRowCount() => RowCount;
    /// <summary>Returns column count alias.</summary>
    public int GetColumnCount() => ColumnCount;
    /// <summary>Returns the zero-based index of the named column, or -1 if not found.</summary>
    public int GetColumnIndex(string headerName) { if (Headers == null) return -1; for (int i = 0; i < Headers.Length; i++) if (string.Equals(Headers[i], headerName, StringComparison.OrdinalIgnoreCase)) return i; return -1; }
    /// <summary>Returns the frequency count of a specific value in the column.</summary>
    public int GetColumnFrequency(string headerName, string value) => GetColumn(headerName).Count(v => v == value);
    /// <summary>Returns the frequency table (value → count) for the column.</summary>
    public Dictionary<string, int> GetFrequencyTable(string headerName) => GetColumnValueCounts(headerName);
    /// <summary>Returns mean alias (non-column-prefix).</summary>
    public double GetMean(string col) => GetColumnMean(col);
    /// <summary>Returns median alias.</summary>
    public double GetMedian(string col) => GetColumnMedian(col);
    /// <summary>Returns std dev alias.</summary>
    public double GetStdDev(string col) => GetColumnStdDev(col);
    /// <summary>Returns kurtosis alias.</summary>
    public double GetKurtosis(string col) => GetColumnKurtosis(col);
    /// <summary>Returns skewness alias.</summary>
    public double GetSkewness(string col) => GetColumnSkewness(col);
    /// <summary>Returns max value alias.</summary>
    public double GetMaxValue(string col) => GetColumnMax(col);
    /// <summary>Returns min value alias.</summary>
    public double GetMinValue(string col) => GetColumnMin(col);
    /// <summary>Returns entropy alias.</summary>
    public double GetEntropy(string col) => GetColumnEntropy(col);
    /// <summary>Returns the string mode alias.</summary>
    public string GetModeValue(string col) => GetColumnMode(col);
    /// <summary>Returns a summary statistics object for the column.</summary>
    public ColumnSummary GetColumnSummary(string headerName) { var v = ParseNumericColumn(GetColumn(headerName)).ToArray(); if (v.Length == 0) return new ColumnSummary { Min = 0, Max = 0, Mean = 0, StdDev = 0 }; double mean = v.Average(); double std = Math.Sqrt(v.Average(x => (x - mean) * (x - mean))); return new ColumnSummary { Min = v.Min(), Max = v.Max(), Mean = mean, StdDev = std }; }
    /// <summary>Returns summary statistics alias.</summary>
    public ColumnSummary GetSummaryStats(string col) => GetColumnSummary(col);
    /// <summary>Returns a histogram bin dictionary for numeric values in the column.</summary>
    public Dictionary<string, int> GetColumnHistogram(string headerName, int bins = 10) { var v = ParseNumericColumn(GetColumn(headerName)).ToArray(); if (v.Length == 0) return new Dictionary<string, int>(); double mn = v.Min(), mx = v.Max(), range = mx - mn; if (range == 0) return new Dictionary<string, int> { [$"{mn:F2}"] = v.Length }; double bw = range / bins; var result = new Dictionary<string, int>(); for (int i = 0; i < bins; i++) { double lo = mn + i * bw, hi = lo + bw; string key = $"[{lo:F2},{hi:F2})"; result[key] = v.Count(x => i < bins - 1 ? x >= lo && x < hi : x >= lo && x <= hi); } return result; }
    /// <summary>Returns per-bin counts for the column histogram.</summary>
    public List<int> GetColumnBinCount(string headerName, int bins = 10) { var v = ParseNumericColumn(GetColumn(headerName)).ToArray(); if (v.Length == 0) return new List<int>(); double mn = v.Min(), mx = v.Max(), range = mx - mn; if (range == 0) return Enumerable.Range(0, bins).Select(i => i == 0 ? v.Length : 0).ToList(); double bw = range / bins; return Enumerable.Range(0, bins).Select(i => { double lo = mn + i * bw, hi = lo + bw; return v.Count(x => i < bins - 1 ? x >= lo && x < hi : x >= lo && x <= hi); }).ToList(); }
    /// <summary>Returns per-bin counts alias (non-column-prefix).</summary>
    public List<int> GetBinCount(string col, int bins = 10) => GetColumnBinCount(col, bins);
    /// <summary>Returns the bin edge values for the histogram.</summary>
    public List<double> GetColumnBinEdges(string headerName, int bins = 10) { var v = ParseNumericColumn(GetColumn(headerName)).ToArray(); if (v.Length == 0) return new List<double>(); double mn = v.Min(), mx = v.Max(), bw = (mx - mn) / bins; return Enumerable.Range(0, bins + 1).Select(i => mn + i * bw).ToList(); }
    /// <summary>Returns per-bin counts as int array.</summary>
    public int[] GetHistogramBins(string col, int bins = 10) => GetColumnBinCount(col, bins).ToArray();
    /// <summary>Returns a filtered copy of the document.</summary>
    public CsvDocument FilterRows(Func<string[], bool> predicate) => Filter(predicate);
    /// <summary>Returns a filtered copy where the named column equals the given value.</summary>
    public CsvDocument Filter(string columnName, string value) { int idx = GetColumnIndex(columnName); return Filter(r => idx >= 0 && idx < r.Length && r[idx] == value); }
    /// <summary>Returns the cell value at the given row and column (alias for GetCellValue).</summary>
    public string? GetCell(int row, int col) => GetCellValue(row, col);
    /// <summary>Deletes the row at the given index.</summary>
    public void DeleteRow(int index) => RemoveRow(index);
    /// <summary>Appends a row (alias for AddRow).</summary>
    public void AppendRow(IEnumerable<string> values) => AddRow(values);
    /// <summary>Sets all cell values in a row.</summary>
    public void SetRowValues(int rowIndex, IEnumerable<string> values) { var arr = values.ToArray(); for (int c = 0; c < arr.Length && c < Rows[rowIndex].Length; c++) Rows[rowIndex][c] = arr[c]; }
    /// <summary>Adds a new column with the given header and values.</summary>
    public void AddColumn(string headerName, IEnumerable<string>? values = null) { var vals = values?.ToArray() ?? Array.Empty<string>(); if (Headers != null) { var newHeaders = Headers.Concat(new[] { headerName }).ToArray(); typeof(CsvDocument).GetProperty("Headers")!.SetValue(this, newHeaders); } for (int i = 0; i < Rows.Count; i++) { var row = Rows[i]; var newRow = new string[row.Length + 1]; Array.Copy(row, newRow, row.Length); newRow[row.Length] = i < vals.Length ? vals[i] : ""; Rows[i] = newRow; } }
    /// <summary>Removes a column by header name.</summary>
    public void RemoveColumn(string headerName) { int idx = GetColumnIndex(headerName); if (idx < 0) return; if (Headers != null) { var h = Headers.ToList(); h.RemoveAt(idx); typeof(CsvDocument).GetProperty("Headers")!.SetValue(this, h.ToArray()); } for (int i = 0; i < Rows.Count; i++) { var r = Rows[i].ToList(); if (idx < r.Count) r.RemoveAt(idx); Rows[i] = r.ToArray(); } }
    /// <summary>Renames a column in place and returns this document.</summary>
    public CsvDocument RenameColumn(string oldName, string newName) { if (Headers != null) for (int i = 0; i < Headers.Length; i++) if (string.Equals(Headers[i], oldName, StringComparison.OrdinalIgnoreCase)) { Headers[i] = newName; break; } return this; }
    /// <summary>Returns a sorted copy of the document by the named column.</summary>
    public CsvDocument SortByColumn(string headerName, bool ascending = true) { int idx = GetColumnIndex(headerName); bool allNum = Rows.All(r => { var v = idx >= 0 && idx < r.Length ? r[idx] : ""; return string.IsNullOrEmpty(v) || double.TryParse(v, System.Globalization.NumberStyles.Any, System.Globalization.CultureInfo.InvariantCulture, out _); }); List<string[]> sorted; if (allNum) { Func<string[], double> numKey = r => { var v = idx >= 0 && idx < r.Length ? r[idx] : ""; return double.TryParse(v, System.Globalization.NumberStyles.Any, System.Globalization.CultureInfo.InvariantCulture, out double d) ? d : double.NaN; }; sorted = ascending ? Rows.OrderBy(numKey).ToList() : Rows.OrderByDescending(numKey).ToList(); } else { sorted = ascending ? Rows.OrderBy(r => idx < r.Length ? r[idx] : "").ToList() : Rows.OrderByDescending(r => idx < r.Length ? r[idx] : "").ToList(); } var doc = new CsvDocument(Headers?.ToArray(), new List<string[]>()); foreach (var row in sorted) doc.AddRow(row); return doc; }
    /// <summary>Sorts rows in place using a key selector.</summary>
    public void SortRows(Func<string[], string[]> keySelector) { var sorted = Rows.OrderBy(r => string.Join(",", keySelector(r))).ToList(); Rows.Clear(); Rows.AddRange(sorted); }
    /// <summary>Sorts rows in place by the named column (numeric if all values parse as numbers) and returns this document.</summary>
    public CsvDocument SortRows(string headerName, bool ascending = true)
    {
        int idx = GetColumnIndex(headerName);
        bool allNumeric = Rows.All(r => {
            var v = idx >= 0 && idx < r.Length ? r[idx] : "";
            return string.IsNullOrEmpty(v) || double.TryParse(v, System.Globalization.NumberStyles.Any, System.Globalization.CultureInfo.InvariantCulture, out _);
        });
        List<string[]> sorted;
        if (allNumeric)
        {
            Func<string[], double> numKey = r => {
                var v = idx >= 0 && idx < r.Length ? r[idx] : "";
                return double.TryParse(v, System.Globalization.NumberStyles.Any, System.Globalization.CultureInfo.InvariantCulture, out double d) ? d : double.NaN;
            };
            sorted = ascending ? Rows.OrderBy(numKey).ToList() : Rows.OrderByDescending(numKey).ToList();
        }
        else
            sorted = ascending ? Rows.OrderBy(r => idx < r.Length ? r[idx] : "").ToList() : Rows.OrderByDescending(r => idx < r.Length ? r[idx] : "").ToList();
        Rows.Clear(); Rows.AddRange(sorted); return this;
    }
    /// <summary>Returns a new document with rows from this and the other merged.</summary>
    public CsvDocument MergeWith(CsvDocument other) { var doc = new CsvDocument(Headers?.ToArray(), new List<string[]>(Rows.Select(r => (string[])r.Clone()))); foreach (var row in other.Rows) doc.AddRow(row); return doc; }
    /// <summary>Returns a shallow clone of this document.</summary>
    public CsvDocument Clone() => new CsvDocument(Headers?.ToArray(), new List<string[]>(Rows.Select(r => (string[])r.Clone())));
    /// <summary>Returns the transposed document (rows become columns).</summary>
    public CsvDocument Transpose() { if (RowCount == 0) return new CsvDocument(null, new List<string[]>()); int cols = Rows.Max(r => r.Length); var transposed = Enumerable.Range(0, cols).Select(c => Rows.Select(r => c < r.Length ? r[c] : "").ToArray()).ToList(); var autoHeaders = Enumerable.Range(0, RowCount).Select(i => "col" + i).ToArray(); return new CsvDocument(autoHeaders, transposed); }
    /// <summary>Returns a pivot table document.</summary>
    public CsvDocument Pivot(string rowCol, string colCol, string valueCol) { var rows = GetDistinctValues(rowCol); var cols = GetDistinctValues(colCol); var headers = new[] { rowCol }.Concat(cols).ToArray(); var data = new List<string[]>(); foreach (var r in rows) { var row = new[] { r }.Concat(cols.Select(c => { var match = Rows.FirstOrDefault(dr => { int ri = GetColumnIndex(rowCol), ci = GetColumnIndex(colCol), vi = GetColumnIndex(valueCol); return ri >= 0 && ci >= 0 && ri < dr.Length && ci < dr.Length && dr[ri] == r && dr[ci] == c; }); if (match == null) return ""; int vi2 = GetColumnIndex(valueCol); return vi2 >= 0 && vi2 < match.Length ? match[vi2] : ""; })).ToArray(); data.Add(row); } return new CsvDocument(headers, data); }
    /// <summary>Returns a random sample of n rows.</summary>
    public CsvDocument GetSampleRows(int n) { var rnd = new Random(); var sampled = Rows.OrderBy(_ => rnd.Next()).Take(n).ToList(); return new CsvDocument(Headers?.ToArray(), sampled); }
    /// <summary>Returns a document with outlier rows removed from the named column.
    /// Outliers are rows whose z-score (standard deviations from the mean) exceeds <paramref name="threshold"/>.
    /// The column statistics are computed once before filtering (O(N), not O(N²)).
    /// </summary>
    public CsvDocument RemoveOutliers(string headerName, double threshold = 3.0)
    {
        int idx = GetColumnIndex(headerName);
        if (idx < 0) return Clone();
        // Compute column statistics ONCE outside the lambda — avoids O(N²) re-parsing per row.
        var vals = ParseNumericColumn(GetColumn(headerName)).ToArray();
        if (vals.Length == 0) return Clone();
        double m = vals.Average();
        double s = Math.Sqrt(vals.Average(x => (x - m) * (x - m)));
        var filtered = Rows.Where(r =>
        {
            if (idx >= r.Length) return true;
            if (!double.TryParse(r[idx], System.Globalization.NumberStyles.Any, System.Globalization.CultureInfo.InvariantCulture, out double v)) return true;
            return s == 0 || Math.Abs((v - m) / s) <= threshold;
        }).ToList();
        return new CsvDocument(Headers?.ToArray(), filtered);
    }
    /// <summary>Exports the document to HTML table format.</summary>
    public string ExportToHtml() => ToHtml();
    /// <summary>Returns an HTML table representation of the document.
    /// All header and cell values are HTML-escaped to prevent XSS injection.
    /// </summary>
    public string ToHtml() { var sb = new System.Text.StringBuilder(); sb.Append("<table>"); if (Headers != null) { sb.Append("<thead><tr>"); foreach (var h in Headers) sb.Append($"<th>{_HtmlEsc(h)}</th>"); sb.Append("</tr></thead>"); } sb.Append("<tbody>"); foreach (var row in Rows) { sb.Append("<tr>"); foreach (var cell in row) sb.Append($"<td>{_HtmlEsc(cell)}</td>"); sb.Append("</tr>"); } sb.Append("</tbody></table>"); return sb.ToString(); }
    private static string _HtmlEsc(string s) =>
        s.Replace("&", "&amp;").Replace("<", "&lt;").Replace(">", "&gt;")
         .Replace("\"", "&quot;").Replace("'", "&#39;");
    /// <summary>Exports to TSV string.</summary>
    public string ExportToTsv() => ToTsv();
    /// <summary>Returns a TSV representation of the document.</summary>
    public string ToTsv() { var sb = new System.Text.StringBuilder(); if (Headers != null) { sb.AppendLine(string.Join("\t", Headers)); } foreach (var row in Rows) sb.AppendLine(string.Join("\t", row)); return sb.ToString(); }
    /// <summary>Exports to JSON string.</summary>
    public string ExportToJson() => ToJson();
    /// <summary>Returns a JSON array representation of the document.</summary>
    public string ToJson() { var sb = new System.Text.StringBuilder(); sb.Append("["); bool first = true; foreach (var row in Rows) { if (!first) sb.Append(","); first = false; sb.Append("{"); bool ff = true; int cols = Math.Min(Headers?.Length ?? row.Length, row.Length); for (int i = 0; i < cols; i++) { if (!ff) sb.Append(","); ff = false; string key = Headers != null && i < Headers.Length ? Headers[i] : $"col{i}"; sb.Append($"\"{_JsonEsc(key)}\":\"{_JsonEsc(row[i])}\""); } sb.Append("}"); } sb.Append("]"); return sb.ToString(); }
    private static string _JsonEsc(string s) =>
        s.Replace("\\", "\\\\").Replace("\"", "\\\"")
         .Replace("\n", "\\n").Replace("\r", "\\r").Replace("\t", "\\t");
    /// <summary>Exports to NDJSON string.</summary>
    public string ExportToNdjson() { var sb = new System.Text.StringBuilder(); foreach (var row in Rows) { sb.Append("{"); bool ff = true; int cols = Math.Min(Headers?.Length ?? row.Length, row.Length); for (int i = 0; i < cols; i++) { if (!ff) sb.Append(","); ff = false; string key = Headers != null && i < Headers.Length ? Headers[i] : $"col{i}"; sb.Append($"\"{_JsonEsc(key)}\":\"{_JsonEsc(row[i])}\""); } sb.AppendLine("}"); } return sb.ToString(); }
    /// <summary>Exports to XML string.</summary>
    public string ExportToXml() { var sb = new System.Text.StringBuilder(); sb.AppendLine("<rows>"); foreach (var row in Rows) { sb.Append("  <row>"); int cols = Math.Min(Headers?.Length ?? row.Length, row.Length); for (int i = 0; i < cols; i++) { string tag = Headers != null && i < Headers.Length ? _XmlTag(Headers[i]) : $"col{i}"; sb.Append($"<{tag}>{_XmlEsc(row[i])}</{tag}>"); } sb.AppendLine("</row>"); } sb.AppendLine("</rows>"); return sb.ToString(); }
    private static string _XmlEsc(string s) => s.Replace("&", "&amp;").Replace("<", "&lt;").Replace(">", "&gt;");
    private static string _XmlTag(string s) { var clean = new string(s.Select(c => char.IsLetterOrDigit(c) || c == '_' ? c : '_').ToArray()); return string.IsNullOrEmpty(clean) || char.IsDigit(clean[0]) ? "_" + clean : clean; }
    /// <summary>Returns Q1, Q2 (median), Q3 for the named column.</summary>
    public QuartilesResult GetColumnQuartiles(string headerName) => new(GetColumnFirstQuartile(headerName), GetColumnMedian(headerName), GetColumnThirdQuartile(headerName));

    /// <summary>Exports to Markdown table string.</summary>
    public string ExportToMarkdown() { var sb = new System.Text.StringBuilder(); if (Headers != null) { sb.AppendLine("| " + string.Join(" | ", Headers) + " |"); sb.AppendLine("| " + string.Join(" | ", Headers.Select(_ => "---")) + " |"); } foreach (var row in Rows) sb.AppendLine("| " + string.Join(" | ", row.Select(c => c.Replace("|", "\\|"))) + " |"); return sb.ToString(); }

    /// <summary>Row count alias (for tests that use .Count directly on the document).</summary>
    public int Count => RowCount;

    /// <summary>Returns a filtered copy where the named column equals the given value (alias for Filter(string,string)).</summary>
    public CsvDocument FilterRows(string columnName, string value) => Filter(columnName, value);

    /// <summary>Returns column values parsed as doubles.</summary>
    public List<double> GetNumericColumn(string col) => ParseNumericColumn(GetColumn(col)).ToList();

    /// <summary>Returns the coefficient of variation (StdDev / Mean) for the column.</summary>
    public double GetCoefficientOfVariation(string col) { double mean = GetColumnMean(col); return mean == 0 ? 0.0 : GetColumnStdDev(col) / Math.Abs(mean); }

    /// <summary>Returns a new document with all rows from this document followed by all rows from other.</summary>
    public CsvDocument Concatenate(CsvDocument other) => MergeWith(other);

    /// <summary>Returns a new document that is an inner join of this and other on the named key column.</summary>
    public CsvDocument JoinWith(CsvDocument other, string keyColumn)
    {
        if (Headers == null || other.Headers == null) return new CsvDocument(null, new List<string[]>());
        int i1 = GetColumnIndex(keyColumn), i2 = other.GetColumnIndex(keyColumn);
        if (i1 < 0 || i2 < 0) return new CsvDocument(null, new List<string[]>());
        var otherNonKey = other.Headers.Where((_, j) => j != i2).ToArray();
        var newHeaders = Headers.Concat(otherNonKey).ToArray();
        var result = new CsvDocument(newHeaders, new List<string[]>());
        foreach (var r1 in Rows)
        {
            if (i1 >= r1.Length) continue;
            string keyVal = r1[i1];
            foreach (var r2 in other.Rows.Where(r => i2 < r.Length && r[i2] == keyVal))
                result.AddRow(r1.Concat(r2.Where((_, j) => j != i2)).ToArray());
        }
        return result;
    }

    /// <summary>Returns summary statistics for all numeric columns as a dictionary keyed by column name.</summary>
    public Dictionary<string, ColumnStats> GetSummaryStats()
    {
        var result = new Dictionary<string, ColumnStats>();
        if (Headers == null) return result;
        for (int i = 0; i < Headers.Length; i++)
        {
            var vals = ParseNumericColumn(GetColumn(i)).ToArray();
            if (vals.Length > 0)
                result[Headers[i]] = GetColumnStats(Headers[i]);
        }
        return result;
    }

    /// <summary>Creates an empty CsvDocument with no headers and no rows.</summary>
    public static CsvDocument CreateEmpty() => new CsvDocument(null, new List<string[]>());

    /// <summary>Creates an empty CsvDocument with the specified headers and no rows.</summary>
    public static CsvDocument CreateEmpty(string[] headers) => new CsvDocument(headers, new List<string[]>());

    /// <summary>Removes all data rows from the document, preserving headers.</summary>
    public void Clear() => Rows.Clear();

    /// <summary>Loads a CsvDocument from a stream.</summary>
    public static CsvDocument LoadStream(Stream stream, bool hasHeaders = true)
    {
        ArgumentNullException.ThrowIfNull(stream);
        using var reader = new StreamReader(stream, System.Text.Encoding.UTF8, detectEncodingFromByteOrderMarks: true, leaveOpen: true);
        var content = reader.ReadToEnd();
        return Load(content, hasHeaders);
    }

    /// <summary>Loads a CsvDocument from a CSV content string (alias for Load).</summary>
    public static CsvDocument LoadContent(string content, bool hasHeaders = true) => Load(content, hasHeaders);

    /// <summary>Returns a new document combining rows from this and the other (alias for MergeWith).</summary>
    public CsvDocument Merge(CsvDocument other) => MergeWith(other);

    /// <summary>Sets a cell value by row index and column name.</summary>
    public void SetCellValue(int row, string columnName, string value)
    {
        var col = GetColumnIndex(columnName);
        if (col < 0) throw new CsvReaderException($"Header '{columnName}' not found.");
        SetCellValue(row, col, value);
    }

    /// <summary>Returns summary statistics for a numeric column.</summary>
    public ColumnStats GetColumnStats(string headerName)
    {
        var vals = ParseNumericColumn(GetColumn(headerName)).ToArray();
        if (vals.Length == 0) return new ColumnStats(0, 0, 0, 0);
        return new ColumnStats(vals.Length, vals.Min(), vals.Max(), vals.Average());
    }
}
