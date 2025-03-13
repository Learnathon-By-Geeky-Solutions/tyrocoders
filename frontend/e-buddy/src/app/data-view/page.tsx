'use client';

import { useState } from 'react';
import * as XLSX from 'xlsx';
import Papa from 'papaparse';

interface DataRow {
  [key: string]: string | number | boolean | null;
}

const DataView: React.FC = () => {
  const [data, setData] = useState<DataRow[]>([]);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
      const fileType = file.name.split('.').pop()?.toLowerCase();

      if (!fileType) {
        alert('Invalid file type!');
        return;
      }

      if (fileType === 'csv') {
        Papa.parse<DataRow>(content, {
          header: true,
          dynamicTyping: true,
          complete: (result) => setData(result.data),
        });
      } else if (fileType === 'xlsx') {
        const workbook = XLSX.read(content, { type: 'binary' });
        const sheetName = workbook.SheetNames[0];
        const sheet = workbook.Sheets[sheetName];
        setData(XLSX.utils.sheet_to_json<DataRow>(sheet));
      } else if (fileType === 'js' || fileType === 'json') {
        try {
          setData(JSON.parse(content));
        } catch (error) {
          alert('Invalid JSON file!');
        }
      } else {
        alert('Unsupported file type!');
      }
    };

    if (file.name.endsWith('.xlsx')) {
      reader.readAsBinaryString(file);
    } else {
      reader.readAsText(file);
    }
  };

  return (
    <div className="bg-white text-gray-900 min-h-screen p-6">
      <h1 className="text-2xl font-bold mb-4">Data Viewer</h1>
      <input
        type="file"
        onChange={handleFileUpload}
        className="mb-4 p-2 border border-gray-300 rounded"
      />
      <div className="overflow-auto border border-gray-300 p-4 rounded-lg">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-gray-300 bg-gray-100">
              {data.length > 0 &&
                Object.keys(data[0]).map((key) => (
                  <th
                    key={key}
                    className="p-2 border border-gray-300 font-semibold text-[#61b33b]"
                  >
                    {key}
                  </th>
                ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, index) => (
              <tr
                key={index}
                className={`border-b border-gray-300 ${
                  index % 2 === 0 ? 'bg-gray-50' : 'bg-white'
                } hover:bg-gray-100`}
              >
                {Object.values(row).map((value, i) => (
                  <td
                    key={i}
                    className="p-2 border border-gray-300"
                    style={{
                      textAlign:
                        typeof value === 'number' ? 'right' : 'left',
                    }}
                  >
                    {String(value)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default DataView;
