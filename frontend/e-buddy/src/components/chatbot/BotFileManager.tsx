import React, { useState } from "react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { FilePlus, FolderOpen, Trash2, Download, Share2 } from "lucide-react";
import FileUploadArea from "../file-upload/FileUploadArea";
import { useToast } from "@/hooks/use-toast";

interface BotFileManagerProps {
  botId: number;
}

export default function BotFileManager({ botId }: BotFileManagerProps) {
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [availableSpace, setAvailableSpace] = useState(100); // 100MB total space
  const { toast } = useToast();

  const handleFilesUploaded = (files: File[]) => {
    setUploadedFiles(files);
    
    // In a real app, you would upload these files to your server
    toast({
      title: "Files uploaded",
      description: `${files.length} files have been uploaded successfully.`,
      duration: 3000,
    });
  };

  // Calculate used space from the files
  const usedSpace = uploadedFiles.reduce((total, file) => total + file.size, 0) / (1024 * 1024);
  const usedPercentage = (usedSpace / availableSpace) * 100;

  return (
    <Card className="shadow-sm">
      <CardHeader className="flex flex-row items-center justify-between py-4">
        <h3 className="text-lg font-semibold">Bot Files & Resources</h3>
        <div className="flex items-center gap-2 text-sm">
          <span className="text-gray-500">
            {usedSpace.toFixed(1)} MB of {availableSpace} MB used
          </span>
          <div className="w-24 h-2 bg-gray-100 rounded-full overflow-hidden">
            <div 
              className="h-full bg-blue-500" 
              style={{ width: `${usedPercentage}%` }}
            />
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="upload" className="w-full">
          <TabsList className="grid w-full grid-cols-2 mb-6">
            <TabsTrigger value="upload">Upload Files</TabsTrigger>
            <TabsTrigger value="manage">Manage Resources</TabsTrigger>
          </TabsList>
          
          <TabsContent value="upload">
            <FileUploadArea 
              onFilesUploaded={handleFilesUploaded}
              maxFiles={10}
              maxSize={20}
            />
          </TabsContent>
          
          <TabsContent value="manage">
            {uploadedFiles.length > 0 ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium">Your Bot Resources</h4>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm">
                      <FolderOpen className="w-4 h-4 mr-2" />
                      New Folder
                    </Button>
                    <Button variant="outline" size="sm">
                      <FilePlus className="w-4 h-4 mr-2" />
                      Add Files
                    </Button>
                  </div>
                </div>
                
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="grid grid-cols-3 text-sm font-medium text-gray-500 pb-2 border-b">
                    <div>Name</div>
                    <div>Size</div>
                    <div>Actions</div>
                  </div>
                  
                  <div className="space-y-2 mt-2">
                    {uploadedFiles.map((file, index) => (
                      <div key={index} className="grid grid-cols-3 py-2 text-sm items-center">
                        <div className="truncate">{file.name}</div>
                        <div>{(file.size / 1024).toFixed(1)} KB</div>
                        <div className="flex gap-2">
                          <button className="p-1 hover:bg-gray-200 rounded">
                            <Download className="w-4 h-4" />
                          </button>
                          <button className="p-1 hover:bg-gray-200 rounded">
                            <Share2 className="w-4 h-4" />
                          </button>
                          <button className="p-1 hover:bg-red-100 text-red-500 rounded">
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-12 bg-gray-50 rounded-lg">
                <FolderOpen className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h4 className="text-lg font-medium">No files yet</h4>
                <p className="text-gray-500 mb-4">Upload files to manage them here</p>
                <Button>Upload Files Now</Button>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
