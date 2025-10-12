import yaml
from pathlib import Path

def load_config(yaml_file):
    with open(yaml_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def generate_author_html(authors):
    """生成作者列表HTML"""
    author_links = []
    for author in authors:
        if author.get('is_me'):
            author_links.append(f"<strong>{author['name']}</strong>")
        elif 'url' in author:
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
        'code': 'code',
        'video': 'video',
        'supplement': 'supplement',
        'data': 'data'
    }
    
    for key, label in link_map.items():
        if key in links:
            link_items.append(f"<a href=\"{links[key]}\">{label}</a>")
    
    return '\n        /\n        '.join(link_items)

def generate_venue_html(pub):
    """生成会议/期刊信息"""
    venue_html = f"<em>{pub['venue']}</em>, {pub['year']}"
    
    if pub.get('oral'):
        venue_html += ' &nbsp <font color="red"><strong>(Oral Presentation)</strong></font>'
    elif pub.get('spotlight'):
        venue_html += ' &nbsp <font color=#FF8080><strong>(Spotlight)</strong></font>'
    
    if pub.get('award'):
        venue_html += f' &nbsp <font color="red"><strong>({pub["award"]})</strong></font>'
    
    return venue_html

def generate_publication_html(pub, index):
    """生成单篇论文的HTML - 静态图片版本"""
    bgcolor = ' bgcolor="#ffffd0"' if pub.get('highlight') else ''
    
    authors_html = generate_author_html(pub['authors'])
    links_html = generate_links_html(pub.get('links', {}))
    venue_html = generate_venue_html(pub)
    
    # 简化版本 - 只用静态图片,不用视频和悬停效果
    html = f'''
    <tr{bgcolor}>
      <td style="padding:16px;width:20%;vertical-align:middle">
        <img src='{pub['image']}' width="160">
      </td>
      <td style="padding:8px;width:80%;vertical-align:middle">
        <a href="{pub['links'].get('project', pub['links'].get('arxiv', '#'))}">
          <span class="papertitle">{pub['title']}</span>
        </a>
        <br>
        {authors_html}
        <br>
        {venue_html}
        <br>
        {links_html}
        <p></p>
        <p>
        {pub['description']}
        </p>
      </td>
    </tr>
'''
    return html

def generate_html(config):
    """生成完整的HTML文件 - 保持原样式"""
    profile = config['profile']
    research = config['research']
    publications = config['publications']
    
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
                <p>
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
                <a href="{profile['photo']}"><img style="width:100%;max-width:100%;object-fit: cover; border-radius: 50%;" alt="profile photo" src="{profile['photo']}" class="hoverZoomLink"></a>
              </td>
            </tr>
          </tbody></table>
          <table style="width:100%;border:0px;border-spacing:0px;border-collapse:separate;margin-right:auto;margin-left:auto;"><tbody>
              <tr>
              <td style="padding:16px;width:100%;vertical-align:middle">
                <h2>Research</h2>
                <p>
                  {research['interests']} Representative works are <span class="highlight">highlighted</span>.
                </p>
              </td>
            </tr>
          </tbody></table>
          <table style="width:100%;border:0px;border-spacing:0px 10px;border-collapse:separate;margin-right:auto;margin-left:auto;"><tbody>

'''
    
    # 生成所有论文
    publications_html = ''
    for i, pub in enumerate(publications):
        publications_html += generate_publication_html(pub, i)
    
    # 底部 - 使用原网站的格式
    footer = '''
          </tbody></table>
          
          <table style="width:100%;border:0px;border-spacing:0px;border-collapse:separate;margin-right:auto;margin-left:auto;"><tbody>
            <tr>
              <td style="padding:0px">
                <br>
                <p style="text-align:right;font-size:small;">
                  Website template from <a href="https://jonbarron.info/">Jon Barron</a>
                </p>
              </td>
            </tr>
          </tbody></table>
        </td>
      </tr>
    </table>
  </body>
</html>
'''
    
    return header + publications_html + footer

def main():
    config = load_config('publications.yaml')
    html_content = generate_html(config)
    
    output_file = Path('index.html')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Successfully generated {output_file}")

if __name__ == '__main__':
    main()