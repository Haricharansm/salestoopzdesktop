export default function CSVUpload() {
  const upload = () => {
    alert("CSV Upload coming next");
  };

  return (
    <div className="card">
      <h2>Upload Leads CSV</h2>
      <input type="file" accept=".csv" />
      <button onClick={upload}>Upload</button>
    </div>
  );
}
