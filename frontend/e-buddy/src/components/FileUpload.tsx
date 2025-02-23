"use client";

import { useState, useCallback } from "react";
import { useDropzone, DropzoneOptions, FileRejection } from "react-dropzone";
import FileItem from "./FileItem";
import { FaCloudUploadAlt } from "react-icons/fa";

const FileUpload: React.FC = () => {
  const [files, setFiles] = useState<File[]>([]);
  const [uploadProgress, setUploadProgress] = useState<Record<string, number>>({});
  const [uploading, setUploading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string>("");

  // Append new files instead of replacing them
  const onDrop = useCallback((acceptedFiles: File[]) => {
    setErrorMessage("");
    setFiles((prevFiles) => [...prevFiles, ...acceptedFiles]);
  }, []);

  // Provide detailed error messages when files are rejected
  const onDropRejected = useCallback((fileRejections: FileRejection[]) => {
    const errorMessages = fileRejections
      .map((rejection) => {
        const fileName = rejection.file.name;
        const errors = rejection.errors
          .map((err) => {
            if (err.code === "file-invalid-type") {
              return "Invalid file type. Only CSV, JSON, SQL, XLSX, or XLS files are allowed.";
            }
            if (err.code === "file-too-large") {
              return "File is too large (max 10MB).";
            }
            return err.message;
          })
          .join(" ");
        return `${fileName}: ${errors}`;
      })
      .join("\n");
    setErrorMessage(errorMessages || "Some files were rejected.");
  }, []);

  // Use an object for the accept prop to strictly allow only specific file types.
  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    onDropRejected,
    accept: {
      "text/csv": [".csv"],
      "application/json": [".json"],
      "application/sql": [".sql"],
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
      "application/vnd.ms-excel": [".xls"],
    },
    multiple: true,
    maxSize: 10 * 1024 * 1024, // 10 MB size limit
  } as DropzoneOptions);

  const handleRemoveFile = (fileToRemove: File) => {
    setFiles((prevFiles) =>
      prevFiles.filter((file) => file.name !== fileToRemove.name)
    );
    setUploadProgress((prev) => {
      const { [fileToRemove.name]: _, ...rest } = prev;
      return rest;
    });
  };

  const saveFileLocally = async (file: File): Promise<void> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const fileData = reader.result as ArrayBuffer;
        const blob = new Blob([fileData], { type: file.type });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = file.name;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        resolve();
      };
      reader.onerror = reject;
      reader.readAsArrayBuffer(file);
    });
  };

  const handleUpload = async (): Promise<void> => {
    setUploading(true);
    for (const file of files) {
      setUploadProgress((prev) => ({ ...prev, [file.name]: 0 }));

      // Simulate upload progress
      for (let progress = 0; progress <= 100; progress += 20) {
        await new Promise((resolve) => setTimeout(resolve, 300));
        setUploadProgress((prev) => ({ ...prev, [file.name]: progress }));
      }

      // Save file locally as a simulation of the upload process
      await saveFileLocally(file);
    }
    setUploading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-r from-blue-50 to-purple-50 flex items-center justify-center p-6">
      <div className="bg-white rounded-lg shadow-lg w-full max-w-2xl p-8">
        <div
          {...getRootProps()}
          className="border-2 border-dashed border-gray-300 rounded-lg p-12 flex flex-col items-center justify-center cursor-pointer hover:border-blue-400 transition duration-300"
        >
          <input {...getInputProps()} />
          <FaCloudUploadAlt className="text-6xl text-blue-400 mb-4" />
          <p className="text-lg font-medium text-gray-600">
            Drag & drop files here, or click to select files
          </p>
          <p className="mt-2 text-sm text-gray-500">
            Only CSV, JSON, SQL, XLSX, or XLS files are allowed (max 10MB).
          </p>
        </div>
        {errorMessage && (
          <pre className="text-red-500 mt-4 whitespace-pre-wrap">
            {errorMessage}
          </pre>
        )}
        <ul className="mt-6 space-y-4">
          {files.map((file) => (
            <FileItem
              key={file.name}
              file={file}
              progress={uploadProgress[file.name] || 0}
              onRemove={handleRemoveFile}
            />
          ))}
        </ul>
        <button
          onClick={handleUpload}
          disabled={uploading || files.length === 0}
          className="mt-6 w-full bg-blue-500 hover:bg-blue-600 text-white font-semibold py-3 rounded-lg transition duration-300 disabled:opacity-50"
        >
          {uploading ? "Uploading..." : "Upload Files"}
        </button>
      </div>
    </div>
  );
};

export default FileUpload;
