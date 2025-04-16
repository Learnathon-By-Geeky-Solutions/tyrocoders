import React, { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Upload, X, File, FileText, Image, FileCheck, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import FilePreview from "./FilePreview";

interface FileUploadAreaProps {
  onFilesUploaded?: (files: File[]) => void;
  maxFiles?: number;
  maxSize?: number; // in MB
  allowedTypes?: string[];
  className?: string;
}

export default function FileUploadArea({
  onFilesUploaded,
  maxFiles = 5,
  maxSize = 10, // 10MB default
  allowedTypes = ["image/*", "application/pdf", ".doc", ".docx", ".xls", ".xlsx", ".txt"],
  className,
}: FileUploadAreaProps) {
  const [files, setFiles] = useState<File[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<{ [key: string]: number }>({});
  const [errors, setErrors] = useState<string[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || []);
    validateAndAddFiles(selectedFiles);
    // Reset the input so the same file can be uploaded again if needed
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const validateAndAddFiles = (selectedFiles: File[]) => {
    const newErrors: string[] = [];
    const validFiles: File[] = [];

    // Check if adding these files would exceed the max number of files
    if (files.length + selectedFiles.length > maxFiles) {
      newErrors.push(`You can only upload a maximum of ${maxFiles} files.`);
      return;
    }

    selectedFiles.forEach((file) => {
      // Check file size
      if (file.size > maxSize * 1024 * 1024) {
        newErrors.push(`${file.name} exceeds the ${maxSize}MB size limit.`);
        return;
      }

      // Check file type
      const fileType = file.type;
      const fileExtension = file.name.split('.').pop()?.toLowerCase();
      const isValidType = allowedTypes.some(type => {
        if (type.startsWith('.')) {
          return `.${fileExtension}` === type;
        } else if (type.includes('*')) {
          const typePrefix = type.split('/')[0];
          return fileType.startsWith(`${typePrefix}/`);
        } else {
          return fileType === type;
        }
      });

      if (!isValidType) {
        newErrors.push(`${file.name} has an unsupported file type.`);
        return;
      }

      validFiles.push(file);
    });

    if (validFiles.length > 0) {
      const newFiles = [...files, ...validFiles];
      setFiles(newFiles);

      // Simulate upload progress
      simulateFileUpload(validFiles);

      if (onFilesUploaded) {
        onFilesUploaded(newFiles);
      }
    }

    setErrors(newErrors);
  };

  const simulateFileUpload = (filesToUpload: File[]) => {
    filesToUpload.forEach(file => {
      const fileId = file.name + file.size;
      setUploadProgress(prev => ({ ...prev, [fileId]: 0 }));

      let progress = 0;
      const interval = setInterval(() => {
        progress += Math.random() * 10;
        if (progress >= 100) {
          progress = 100;
          clearInterval(interval);
        }
        setUploadProgress(prev => ({ ...prev, [fileId]: progress }));
      }, 200);
    });
  };

  const removeFile = (index: number) => {
    const newFiles = [...files];
    newFiles.splice(index, 1);
    setFiles(newFiles);

    if (onFilesUploaded) {
      onFilesUploaded(newFiles);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);

    const droppedFiles = Array.from(e.dataTransfer.files);
    validateAndAddFiles(droppedFiles);
  };

  return (
    <div className={cn("space-y-4", className)}>
      {/* Error messages */}
      {errors.length > 0 && (
        <div className="bg-red-50 text-red-600 p-3 rounded-md">
          <div className="flex items-center gap-2 font-medium mb-1">
            <AlertCircle className="w-4 h-4" />
            <span>Upload errors</span>
          </div>
          <ul className="list-disc list-inside space-y-1 text-sm">
            {errors.map((error, index) => (
              <li key={index}>{error}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Drop zone */}
      <div 
        className={cn(
          "border-2 border-dashed rounded-lg p-8 transition-colors text-center",
          isDragging 
            ? "border-primary bg-primary/5" 
            : "border-gray-300 hover:border-gray-400 bg-gray-50/50",
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="flex flex-col items-center justify-center space-y-4">
          <div className="p-3 rounded-full bg-primary/10">
            <Upload className="w-6 h-6 text-primary" />
          </div>
          <div className="space-y-1">
            <p className="font-medium">
              Drag files here or <span className="text-primary">browse</span>
            </p>
            <p className="text-sm text-gray-500">
              Upload up to {maxFiles} files (max {maxSize}MB each)
            </p>
            <p className="text-xs text-gray-400">
              Supported formats: Images, PDFs, DOC, DOCX, XLS, XLSX, TXT
            </p>
          </div>
          <Button
            type="button"
            variant="outline"
            onClick={() => fileInputRef.current?.click()}
          >
            Select Files
          </Button>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            onChange={handleFileChange}
            className="hidden"
            accept={allowedTypes.join(",")}
          />
        </div>
      </div>

      {/* File preview list */}
      {files.length > 0 && (
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <h4 className="font-medium">Uploaded Files</h4>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => setFiles([])}
              className="text-red-500 hover:text-red-700 hover:bg-red-50"
            >
              Remove All
            </Button>
          </div>
          <div className="space-y-2">
            {files.map((file, index) => (
              <FilePreview 
                key={index} 
                file={file} 
                progress={uploadProgress[file.name + file.size] || 0}
                onRemove={() => removeFile(index)} 
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
