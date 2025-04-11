import React from "react";
import { Progress } from "@/components/ui/progress";
import { X, File, FileText, Image, Music, FileArchive, Video } from "lucide-react";
import { cn } from "@/lib/utils";

interface FilePreviewProps {
  file: File;
  progress: number;
  onRemove: () => void;
  className?: string;
}

export default function FilePreview({ file, progress, onRemove, className }: FilePreviewProps) {
  const isUploading = progress < 100;
  const fileSize = formatFileSize(file.size);
  
  // Determine file icon based on file type
  const FileIcon = getFileIcon(file);

  return (
    <div className={cn("flex items-center justify-between p-3 bg-gray-50 rounded-lg group", className)}>
      <div className="flex items-center gap-3 overflow-hidden">
        <div className="flex-shrink-0 p-2 bg-white rounded-md shadow-sm">
          <FileIcon className="w-5 h-5 text-primary" />
        </div>
        <div className="min-w-0 flex-1">
          <p className="font-medium truncate">{file.name}</p>
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <span>{fileSize}</span>
            {isUploading && (
              <span className="text-blue-600">{Math.round(progress)}%</span>
            )}
          </div>
          {isUploading && (
            <Progress value={progress} className="h-1 mt-1 w-full" />
          )}
        </div>
      </div>
      <button 
        onClick={onRemove}
        className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-gray-200 rounded-full ml-2"
        aria-label="Remove file"
      >
        <X className="w-4 h-4 text-gray-500" />
      </button>
    </div>
  );
}

function getFileIcon(file: File) {
  const type = file.type;
  
  if (type.startsWith('image/')) {
    return Image;
  } else if (type.startsWith('video/')) {
    return Video;
  } else if (type.startsWith('audio/')) {
    return Music;
  } else if (type.includes('zip') || type.includes('archive') || type.includes('compressed')) {
    return FileArchive;
  } else if (type.includes('pdf') || type.includes('document') || type.includes('text')) {
    return FileText;
  } else {
    return File;
  }
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}
