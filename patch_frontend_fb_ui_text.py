import sys

path = r'C:\Users\PC8\Downloads\Sevenunique_AI_Frontend\SU_AI_Frontend\app\(dashboard)\content-library\page.tsx'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

target = """                    ) : (
                      <div className="space-y-3 bg-white p-3 rounded-md border border-blue-200 shadow-sm animate-in fade-in">
                        <p className="text-xs font-medium text-red-600">Please register API credentials.</p>
                        <div>
                          <Label className="text-[10px]">Facebook Page ID</Label>"""

replacement = """                    ) : (
                      <div className="space-y-3 bg-white p-3 rounded-md border border-blue-200 shadow-sm animate-in fade-in">
                        <div className="text-[10px] text-blue-900 bg-blue-50 p-2 rounded">
                          <strong>Don't have a Facebook Page?</strong> <br/>
                          <a href="https://www.facebook.com/pages/create/" target="_blank" rel="noreferrer" className="text-blue-600 underline">Click here to create one</a>.
                        </div>
                        <p className="text-[10px] font-medium text-red-600">Please register your API credentials.</p>
                        <div>
                          <Label className="text-[10px]">Facebook Page ID</Label>"""

content = content.replace(target, replacement)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
