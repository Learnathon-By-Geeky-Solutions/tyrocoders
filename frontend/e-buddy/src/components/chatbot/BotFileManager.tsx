import React, { useState } from "react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  FilePlus,
  FolderOpen,
  Trash2,
  Download,
  Share2,
  File,
  Globe,
  Plus,
} from "lucide-react";
import FileUploadArea from "./FileUploadArea";
import { useToast } from "@/hooks/use-toast";

interface BotFileManagerProps {
  botId: string;
}

interface Source {
  title: string;
  url: string;
}

export default function BotFileManager({ botId }: BotFileManagerProps) {
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [availableSpace, setAvailableSpace] = useState(100); // 100MB total space

  const [sources, setSources] = useState<Source[]>([{ title: "", url: "" }]);

  const addSource = (): void =>
    setSources([...sources, { title: "", url: "" }]);

  const updateSource = (
    index: number,
    field: keyof Source,
    value: string
  ): void => {
    const updated = [...sources];
    updated[index] = { ...updated[index], [field]: value };
    setSources(updated);
  };

  const removeSource = (index: number): void => {
    setSources(sources.filter((_, i) => i !== index));
  };

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
        <h3 className="text-lg font-semibold">Add knowledge source</h3>
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
        <Tabs defaultValue="file" className="w-full">
          <TabsList className="grid w-full grid-cols-2 mb-6">
            <TabsTrigger
              value="file"
              className="flex items-center justify-center space-x-2"
            >
              <File className="h-4 w-4" />
              <span>File</span>
            </TabsTrigger>
            <TabsTrigger
              value="webpage"
              className="flex items-center justify-center space-x-2"
            >
              <Globe className="h-4 w-4" />
              <span>Webpage</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="file">
            <FileUploadArea
              onFilesUploaded={handleFilesUploaded}
              maxFiles={10}
              maxSize={20}
              botId={botId}
            />
          </TabsContent>

          <TabsContent value="webpage">
            <div className="space-y-4">
              {sources.map((source, idx) => (
                <div key={idx} className="flex items-center space-x-2">
                  <Input
                    placeholder="Source Title"
                    value={source.title}
                    onChange={(e) => updateSource(idx, "title", e.target.value)}
                    className="flex-1"
                  />
                  <Input
                    placeholder="Source URL"
                    value={source.url}
                    onChange={(e) => updateSource(idx, "url", e.target.value)}
                    className="flex-1"
                  />
                  {sources.length > 1 && (
                    <Button
                      size="icon"
                      variant="destructive"
                      onClick={() => removeSource(idx)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              ))}
              <Button
                variant="outline"
                size="sm"
                className="flex items-center space-x-1"
                onClick={addSource}
              >
                <Plus className="h-4 w-4" />
                <span>Add another source</span>
              </Button>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
