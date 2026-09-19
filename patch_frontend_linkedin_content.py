import sys

path = r'C:\Users\PC8\Downloads\Sevenunique_AI_Frontend\SU_AI_Frontend\app\(dashboard)\content-library\page.tsx'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update imports
target_import = "import { Library, Sparkles, Send, Instagram, Facebook } from 'lucide-react';"
replace_import = "import { Library, Sparkles, Send, Instagram, Facebook, Linkedin } from 'lucide-react';"
content = content.replace(target_import, replace_import)

# 2. Update state variables
target_state = """  // Facebook State
  const [isPublishingFb, setIsPublishingFb] = useState(false);"""
replace_state = """  // LinkedIn State
  const [isPublishingLi, setIsPublishingLi] = useState(false);
  const [showLiRegister, setShowLiRegister] = useState(false);
  const [liRegAuthorId, setLiRegAuthorId] = useState("");
  const [liRegToken, setLiRegToken] = useState("");
  const [isRegisteringLi, setIsRegisteringLi] = useState(false);

  // Facebook State
  const [isPublishingFb, setIsPublishingFb] = useState(false);"""
content = content.replace(target_state, replace_state)

# 3. Add handlePublishLi and handleLiRegisterAndPublish
target_func = """  // Facebook Publishing Flow"""
replace_func = """  // LinkedIn Publishing Flow
  const handlePublishLi = async () => {
    if (!selectedContent) return;
    setIsPublishingLi(true);
    try {
      await socialService.publishToLinkedin(selectedContent._id);
      alert("Successfully published to LinkedIn!");
      setShowLiRegister(false);
    } catch (error: any) {
      const msg = error.response?.data?.detail || error.message;
      if (msg.toLowerCase().includes("not connected")) {
        setShowLiRegister(true);
      } else {
        alert("Failed to publish: " + msg);
      }
    } finally {
      setIsPublishingLi(false);
    }
  };

  const handleLiRegisterAndPublish = async () => {
    setIsRegisteringLi(true);
    try {
      await api.put('/api/v1/business', {
        linkedin_author_id: liRegAuthorId,
        linkedin_access_token: liRegToken
      });
      setShowLiRegister(false);
      await handlePublishLi();
    } catch (error) {
      alert("Failed to register LinkedIn credentials");
    } finally {
      setIsRegisteringLi(false);
    }
  };

  // Facebook Publishing Flow"""
content = content.replace(target_func, replace_func)

# 4. Update the Grid to 4 columns and add LinkedIn section
target_grid = """<div className="grid md:grid-cols-3 gap-4 mt-4">"""
replace_grid = """<div className="grid md:grid-cols-4 gap-4 mt-4">"""
content = content.replace(target_grid, replace_grid)

target_ui = """                </div>
                
            </div>
          </div>
        </div>"""
replace_ui = """                  {/* LinkedIn Publish Section */}
                  <div className="p-4 border-t md:border-t-0 md:border-l bg-blue-50/50">
                    <h3 className="font-semibold text-blue-900 mb-2">LinkedIn</h3>
                    <p className="text-xs text-blue-800 mb-4">Post directly to your network.</p>
                    
                    {!showLiRegister ? (
                      <Button onClick={handlePublishLi} disabled={isPublishingLi} className="w-full bg-blue-700 hover:bg-blue-800 h-8 text-xs">
                        {isPublishingLi ? <Loader2 className="h-3 w-3 animate-spin" /> : <Linkedin className="h-3 w-3 mr-2" />}
                        Publish Post
                      </Button>
                    ) : (
                      <div className="space-y-3 bg-white p-3 rounded-md border border-blue-200 shadow-sm animate-in fade-in">
                        <div className="text-[10px] text-blue-900 bg-blue-50 p-2 rounded">
                          <strong>Don't have a Developer App?</strong> <br/>
                          <a href="https://www.linkedin.com/developers/" target="_blank" rel="noreferrer" className="text-blue-600 underline">Click here to create one</a>.
                        </div>
                        <p className="text-[10px] font-medium text-red-600">Please register your API credentials.</p>
                        <div>
                          <Label className="text-[10px]">Author ID (urn:li:person:...)</Label>
                          <Input value={liRegAuthorId} onChange={(e) => setLiRegAuthorId(e.target.value)} className="mt-1 h-7 text-xs" />
                        </div>
                        <div>
                          <Label className="text-[10px]">Access Token</Label>
                          <Input type="password" value={liRegToken} onChange={(e) => setLiRegToken(e.target.value)} className="mt-1 h-7 text-xs" />
                        </div>
                        <div className="flex gap-2">
                          <Button onClick={handleLiRegisterAndPublish} disabled={isRegisteringLi} className="w-full h-7 text-[10px] bg-blue-700 hover:bg-blue-800 px-1">
                            {isRegisteringLi ? <Loader2 className="h-3 w-3 animate-spin mr-1" /> : null} Save & Publish
                          </Button>
                          <Button variant="outline" onClick={() => setShowLiRegister(false)} className="h-7 text-[10px] px-2">Cancel</Button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
                
            </div>
          </div>
        </div>"""
content = content.replace(target_ui, replace_ui)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
