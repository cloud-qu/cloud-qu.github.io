import yaml
from pathlib import Path
from collections import defaultdict

def load_config(yaml_file):
    with open(yaml_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def generate_author_html(authors):
    """生成作者列表HTML"""
    author_links = []
    for author in authors:
        if author.get('is_me'):
            author_links.append(f"<strong style='color:#000;'>{author['name']}</strong>")
        elif 'url' in author and author['url']:
            author_links.append(f"<a href=\"{author['url']}\">{author['name']}</a>")
        else:
            author_links.append(author['name'])
    return ',\n        '.join(author_links)

def generate_links_html(links):
    """生成论文链接HTML"""
    link_items = []
    link_map = {
        'project': 'project page',
        'paper': 'paper',
        'arxiv': 'arXiv',
        'code': 'code',
        'video': 'video',
        'supplement': 'supplement',
        'data': 'data'
    }
    
    for key, label in link_map.items():
        if key in links and links[key]:
            link_items.append(f"<a href=\"{links[key]}\">{label}</a>")
    
    return '\n        /\n        '.join(link_items)

def generate_venue_html(pub):
    """生成会议/期刊信息"""
    venue_html = f"<em>{pub['venue']}</em>, {pub['year']}"
    
    if pub.get('oral'):
        venue_html += ' &nbsp;<font color="red"><strong>(Oral)</strong></font>'
    elif pub.get('spotlight'):
        venue_html += ' &nbsp;<font color="#FF8080"><strong>(Spotlight)</strong></font>'
    
    if pub.get('award'):
        venue_html += f' &nbsp;<font color="red"><strong>{pub["award"]}</strong></font>'
    
    return venue_html

def generate_news_html(news_items):
    """生成新闻模块HTML - 简约版"""
    if not news_items:
        return ""
    
    news_html = '''          <table style="width:100%;border:0px;border-spacing:0px;border-collapse:separate;margin-right:auto;margin-left:auto;"><tbody>
            <tr>
              <td style="padding:20px;width:100%;vertical-align:middle">
                <h2 style="border-bottom:2px solid #e0e0e0;padding-bottom:10px;">News</h2>
                <div style="max-height:200px;overflow-y:auto;margin-top:15px;">
                <ul style="margin:0;padding-left:20px;">
'''
    
    for item in news_items:
        date_str = f"<strong style='color:#2c5aa0;'>[{item['date']}]</strong> " if 'date' in item else ""
        news_html += f"                  <li style='margin-bottom:10px;line-height:1.6;'>{date_str}{item['content']}</li>\n"
    
    news_html += '''                </ul>
                </div>
              </td>
            </tr>
          </tbody></table>
'''
    return news_html
def generate_publication_html(pub, index):
    """生成单篇论文的HTML - 带灯箱效果"""
    bgcolor = ' bgcolor="#ffffd0"' if pub.get('highlight') else ''
    
    authors_html = generate_author_html(pub['authors'])
    links_html = generate_links_html(pub.get('links', {}))
    venue_html = generate_venue_html(pub)
    
    # 处理图片：无图时显示占位符
    image = pub.get('image', '')
    if image:
        img_html = f'''<div style="border-radius:4px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.12);">
          <img src='{image}' width="160" style="width:100%;display:block;cursor:pointer;transition:transform 0.2s;" 
               onmouseover="this.style.transform='scale(1.05)'" 
               onmouseout="this.style.transform='scale(1)'"
               onclick="openLightbox('{image}')">
        </div>'''
    else:
        img_html = '''<div style="border-radius:4px;overflow:hidden;width:160px;height:100px;background:#f0f0f0;display:flex;align-items:center;justify-content:center;">
          <span style="color:#ccc;font-size:28px;">📄</span>
        </div>'''
    
    # 处理论文标题链接
    links = pub.get('links', {})
    title_url = links.get('project', '') or links.get('arxiv', '') or links.get('paper', '') or '#'
    
    # 处理链接行
    links_line = f'''<br>
        <span style="font-size:14px;">
        {links_html}
        </span>''' if links_html else ''
    
    html = f'''
    <tr{bgcolor}>
      <td style="padding:20px;width:25%;vertical-align:middle">
        {img_html}
      </td>
      <td style="padding:20px;width:75%;vertical-align:middle">
        <a href="{title_url}">
          <span class="papertitle">{pub['title']}</span>
        </a>
        <br>
        <span style="font-size:14px;color:#555;">
        {authors_html}
        </span>
        <br>
        {venue_html}
        {links_line}
        <p></p>
        <p style="color:#666;font-size:14px;line-height:1.5;">
        {pub['description']}
        </p>
      </td>
    </tr>
'''
    return html

def generate_publications_by_year(publications):
    """按年份分组生成论文HTML，支持折叠展开"""
    # 按年份分组
    pubs_by_year = defaultdict(list)
    for pub in publications:
        pubs_by_year[pub['year']].append(pub)
    
    # 按年份降序排列
    sorted_years = sorted(pubs_by_year.keys(), reverse=True)
    
    html = ''
    for year in sorted_years:
        year_pubs = pubs_by_year[year]
        count = len(year_pubs)
        
        html += f'''
          <table style="width:100%;border:0px;border-spacing:0px;border-collapse:separate;margin-right:auto;margin-left:auto;"><tbody>
            <tr>
              <td style="padding:10px 20px;width:100%;vertical-align:middle;">
                <div onclick="toggleYear('{year}')" style="cursor:pointer;display:flex;align-items:center;user-select:none;">
                  <span id="arrow-{year}" style="display:inline-block;transition:transform 0.3s;transform:rotate(90deg);margin-right:10px;font-size:14px;color:#999;">&#9654;</span>
                  <h3 style="margin:0;color:#333;font-weight:600;font-size:18px;">{year}</h3>
                  <span style="margin-left:10px;color:#999;font-size:14px;">({count} paper{"s" if count > 1 else ""})</span>
                </div>
              </td>
            </tr>
          </tbody></table>
          <table id="year-{year}" style="width:100%;border:0px;border-spacing:0px 10px;border-collapse:separate;margin-right:auto;margin-left:auto;"><tbody>
'''
        for i, pub in enumerate(year_pubs):
            html += generate_publication_html(pub, i)
        
        html += '''
          </tbody></table>
'''
    
    return html

def generate_miscellaneous_html(misc_items):
    """生成杂项模块HTML - 简约版"""
    if not misc_items:
        return ""
    
    misc_html = '''          <table style="width:100%;border:0px;border-spacing:0px;border-collapse:separate;margin-right:auto;margin-left:auto;"><tbody>
            <tr>
              <td style="padding:20px;width:100%;vertical-align:middle">
                <h2 style="border-bottom:2px solid #e0e0e0;padding-bottom:10px;">Miscellaneous</h2>
'''
    
    for section in misc_items:
        if 'title' in section:
            misc_html += f"                <h3 style='color:#333;margin-top:20px;margin-bottom:10px;font-weight:600;'>{section['title']}</h3>\n"
        
        if 'content' in section:
            misc_html += f"                <p style='color:#666;line-height:1.7;margin:10px 0;'>{section['content']}</p>\n"
        
        if 'items' in section:
            misc_html += "                <ul style='line-height:1.8;margin:10px 0;padding-left:20px;'>\n"
            for item in section['items']:
                if isinstance(item, dict):
                    label = f"<strong style='color:#2c5aa0;'>{item.get('label', '')}</strong>: " if item.get('label') else ""
                    text = item.get('text', '')
                    item_html = f"{label}{text}"
                    if 'link' in item:
                        item_html = f"<a href=\"{item['link']}\">{item_html}</a>"
                    misc_html += f"                  <li style='color:#555;margin-bottom:8px;'>{item_html}</li>\n"
                else:
                    misc_html += f"                  <li style='color:#555;margin-bottom:8px;'>{item}</li>\n"
            misc_html += "                </ul>\n"
    
    misc_html += '''              </td>
            </tr>
          </tbody></table>
'''
    return misc_html

# def generate_lightbox_html():
#     """生成灯箱HTML和JavaScript"""
#     return '''
#     <!-- Lightbox Modal -->
#     <div id="lightbox" style="display:none;position:fixed;z-index:9999;left:0;top:0;width:100%;height:100%;background-color:rgba(0,0,0,0.9);cursor:pointer;" onclick="closeLightbox()">
#       <span style="position:absolute;top:20px;right:40px;color:#f1f1f1;font-size:40px;font-weight:bold;cursor:pointer;" onclick="closeLightbox()">&times;</span>
#       <img id="lightbox-img" style="margin:auto;display:block;max-width:90%;max-height:90%;position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);box-shadow:0 4px 20px rgba(0,0,0,0.5);">
#     </div>
    
#     <script>
#     function openLightbox(imgSrc) {
#       event.stopPropagation();
#       document.getElementById('lightbox').style.display = 'block';
#       document.getElementById('lightbox-img').src = imgSrc;
#       document.body.style.overflow = 'hidden';
#     }
    
#     function closeLightbox() {
#       document.getElementById('lightbox').style.display = 'none';
#       document.body.style.overflow = 'auto';
#     }
    
#     function toggleYear(year) {
#       var content = document.getElementById('year-' + year);
#       var arrow = document.getElementById('arrow-' + year);
#       if (content.style.display === 'none') {
#         content.style.display = '';
#         arrow.style.transform = 'rotate(90deg)';
#       } else {
#         content.style.display = 'none';
#         arrow.style.transform = 'rotate(0deg)';
#       }
#     }
    
#     // 按ESC键关闭灯箱
#     document.addEventListener('keydown', function(e) {
#       if (e.key === 'Escape') {
#         closeLightbox();
#       }
#     });
#     </script>
# '''

def generate_lightbox_html():
    """生成灯箱HTML和JavaScript"""
    return '''
    <!-- Lightbox Modal -->
    <div id="lightbox" style="display:none;position:fixed;z-index:9999;left:0;top:0;width:100%;height:100%;background-color:rgba(0,0,0,0.9);cursor:pointer;" onclick="closeLightbox()">
      <span style="position:absolute;top:20px;right:40px;color:#f1f1f1;font-size:40px;font-weight:bold;cursor:pointer;" onclick="closeLightbox()">&times;</span>
      <img id="lightbox-img" style="margin:auto;display:block;max-width:90%;max-height:90%;position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);box-shadow:0 4px 20px rgba(0,0,0,0.5);">
    </div>
    
    <!-- 返回顶部按钮 -->
    <button id="back-to-top" onclick="window.scrollTo({top:0,behavior:\'smooth\'})" 
            style="display:none;position:fixed;bottom:30px;right:30px;z-index:999;border:none;outline:none;background-color:#2c5aa0;color:white;cursor:pointer;padding:12px 16px;border-radius:50%;font-size:18px;box-shadow:0 2px 10px rgba(0,0,0,0.2);transition:opacity 0.3s,transform 0.3s;"
            onmouseover="this.style.transform=\'scale(1.1)\'" 
            onmouseout="this.style.transform=\'scale(1)\'">↑</button>
    
    <script>
    function openLightbox(imgSrc) {
      event.stopPropagation();
      document.getElementById('lightbox').style.display = 'block';
      document.getElementById('lightbox-img').src = imgSrc;
      document.body.style.overflow = 'hidden';
    }
    
    function closeLightbox() {
      document.getElementById('lightbox').style.display = 'none';
      document.body.style.overflow = 'auto';
    }
    
    function toggleYear(year) {
      var content = document.getElementById('year-' + year);
      var arrow = document.getElementById('arrow-' + year);
      if (content.style.display === 'none') {
        content.style.display = '';
        arrow.style.transform = 'rotate(90deg)';
      } else {
        content.style.display = 'none';
        arrow.style.transform = 'rotate(0deg)';
      }
    }
    
    // 按ESC键关闭灯箱
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') {
        closeLightbox();
      }
    });
    
    // 返回顶部按钮显示/隐藏
    window.onscroll = function() {
      var btn = document.getElementById('back-to-top');
      if (document.body.scrollTop > 300 || document.documentElement.scrollTop > 300) {
        btn.style.display = 'block';
      } else {
        btn.style.display = 'none';
      }
    };
    </script>
'''

def generate_html(config):
    """生成完整的HTML文件 - 简约大气版"""
    profile = config['profile']
    news = config.get('news', [])
    research = config['research']
    publications = config['publications']
    miscellaneous = config.get('miscellaneous', [])
    
    # 使用原网站的完整头部
    header = f'''<!DOCTYPE HTML>
<html lang="en">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

    <title>{profile['name']}</title>

    <meta name="author" content="{profile['name']}">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="shortcut icon" href="images/favicon/favicon.ico" type="image/x-icon">
    <link rel="stylesheet" type="text/css" href="stylesheet.css">
    
  </head>

  <body>
    <table style="width:100%;max-width:800px;border:0px;border-spacing:0px;border-collapse:separate;margin-right:auto;margin-left:auto;"><tbody>
      <tr style="padding:0px">
        <td style="padding:0px">
          <table style="width:100%;border:0px;border-spacing:0px;border-collapse:separate;margin-right:auto;margin-left:auto;"><tbody>
            <tr style="padding:0px">
              <td style="padding:2.5%;width:63%;vertical-align:middle">
                <p class="name" style="text-align: center;">
                  {profile['name']}
                </p>
                <p style="line-height:1.7;">
                  I'm a {profile['title']} in the {profile['department']} at <a href="{profile['institution_url']}">{profile['institution']}</a>, advised by <a href="{profile['advisor_url']}">{profile['advisor']}</a>.
                  {profile['bio']}
                </p>
                <p style="text-align:center">
                  <a href="mailto:{profile['email']}">Email</a> &nbsp;/&nbsp;
                  <a href="{profile['scholar']}">Scholar</a> &nbsp;/&nbsp;
                  <a href="{profile['twitter']}">Twitter</a> &nbsp;/&nbsp;
                  <a href="{profile['github']}">Github</a>
                </p>
              </td>
              <td style="padding:2.5%;width:37%;max-width:37%">
                <img style="width:100%;max-width:100%;object-fit: cover; border-radius: 50%;box-shadow:0 2px 8px rgba(0,0,0,0.15);" alt="profile photo" src="{profile['photo']}">
              </td>
            </tr>
          </tbody></table>
'''

    
    # 添加News模块
    news_html = generate_news_html(news)
    total_pubs = len(publications)
    research_header = f'''          <table style="width:100%;border:0px;border-spacing:0px;border-collapse:separate;margin-right:auto;margin-left:auto;"><tbody>
              <tr>
              <td style="padding:20px;width:100%;vertical-align:middle">
                <h2 style="border-bottom:2px solid #e0e0e0;padding-bottom:10px;">Research 
                  <span style="font-size:14px;color:#999;font-weight:normal;margin-left:8px;">({total_pubs} publications)</span>
                </h2>
                <p style="line-height:1.7;color:#555;margin-top:15px;">
                  {research['interests']}
                </p>
              </td>
            </tr>
          </tbody></table>
'''
    
#     # Research部分
#     research_header = f'''          <table style="width:100%;border:0px;border-spacing:0px;border-collapse:separate;margin-right:auto;margin-left:auto;"><tbody>
#               <tr>
#               <td style="padding:20px;width:100%;vertical-align:middle">
#                 <h2 style="border-bottom:2px solid #e0e0e0;padding-bottom:10px;">Research</h2>
#                 <p style="line-height:1.7;color:#555;margin-top:15px;">
#                   {research['interests']}
#                 </p>
#               </td>
#             </tr>
#           </tbody></table>
# '''
    
    # 按年份分组生成论文
    publications_html = generate_publications_by_year(publications)
    
    # 添加Miscellaneous模块
    misc_html = generate_miscellaneous_html(miscellaneous)
    
    # 添加灯箱
    lightbox_html = generate_lightbox_html()
    
    # 底部 - 使用原网站的格式
    footer = '''          
          <table style="width:100%;border:0px;border-spacing:0px;border-collapse:separate;margin-right:auto;margin-left:auto;"><tbody>
            <tr>
              <td style="padding:0px">
                <br>
                <p style="text-align:right;font-size:small;color:#999;">
                  Website template from <a href="https://jonbarron.info/" style="color:#999;">Jon Barron</a>
                </p>
              </td>
            </tr>
          </tbody></table>
        </td>
      </tr>
    </table>
'''
    
    return header + news_html + research_header + publications_html + misc_html + lightbox_html + footer + '''
  </body>
</html>'''

def main():
    config = load_config('publications.yaml')
    html_content = generate_html(config)
    
    output_file = Path('index.html')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Successfully generated {output_file}")

if __name__ == '__main__':
    main()