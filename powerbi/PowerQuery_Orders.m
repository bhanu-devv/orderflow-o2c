// Power BI Desktop: create a parameter named DataFolder (Text), containing the absolute path to /data.
// Other CSVs can be loaded with the same pattern and correct type conversions.
let
    Source = Csv.Document(File.Contents(DataFolder & "orders.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{"order_id", type text},{"customer_id", type text},{"sku", type text},{"order_date", type date},{"promised_date", type date},{"ordered_qty", Int64.Type},{"unit_price", type number},{"order_amount", type number},{"status", type text},{"priority", type text}})
in
    Typed
