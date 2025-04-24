// app/components/FileItem.tsx
"use client";
import React from "react";
import {
  FaFileAlt,
  FaFileExcel,
  FaFileCode,
  FaDatabase,
  FaTimes,
} from "react-icons/fa";
import ProgressBar from "../components/ProgressBar";

interface FileItemProps {
  file: File;
  progress: number;
  onRemove: (file: File) => void;
}

const getFileIcon = (fileName: string) => {
  const ext = fileName.split(".").pop()?.toLowerCase();
  switch (ext) {
    case "csv":
    case "xlsx":
    case "xls":
      return <FaFileExcel className="mr-2 text-green-500 text-2xl" />;
    case "json":
      return <FaFileCode className="mr-2 text-purple-500 text-2xl" />;
    case "sql":
      return <FaDatabase className="mr-2 text-orange-500 text-2xl" />;
    default:
      return <FaFileAlt className="mr-2 text-gray-500 text-2xl" />;
  }
};

const FileItem: React.FC<FileItemProps> = ({ file, progress, onRemove }) => {
  return (
    <li
      key={file.name}
      className="bg-gray-50 p-4 rounded-lg shadow-sm flex flex-col"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          {getFileIcon(file.name)}
          <span className="font-medium text-gray-700">{file.name}</span>
        </div>
        <button
          onClick={() => onRemove(file)}
          className="text-red-500 hover:text-red-700"
          aria-label={`Remove ${file.name}`}
        >
          <FaTimes />
        </button>
      </div>
      <div className="mt-2">
        <ProgressBar progress={progress} />
      </div>
    </li>
  );
};

export default FileItem;
