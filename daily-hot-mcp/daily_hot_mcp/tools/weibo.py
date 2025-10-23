"""微博工具集 - 包含热搜、搜索、用户信息等功能"""

import asyncio
from urllib.parse import urlencode
from daily_hot_mcp.utils import http_client
from fastmcp.tools import Tool

# 导入其他微博工具
try:
    from .weibo_search import (
        search_weibo_content, 
        search_weibo_topics, 
        search_weibo_users,
        weibo_search_tools
    )
    from .weibo_user import (
        get_weibo_user_profile,
        get_weibo_user_feeds,
        get_weibo_user_followers,
        get_weibo_user_fans,
        weibo_user_tools
    )
    from .weibo_comments import (
        get_weibo_comments,
        get_weibo_hot_feeds,
        weibo_comments_tools
    )
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    from weibo_search import (
        search_weibo_content, 
        search_weibo_topics, 
        search_weibo_users,
        weibo_search_tools
    )
    from weibo_user import (
        get_weibo_user_profile,
        get_weibo_user_feeds,
        get_weibo_user_followers,
        get_weibo_user_fans,
        weibo_user_tools
    )
    from weibo_comments import (
        get_weibo_comments,
        get_weibo_hot_feeds,
        weibo_comments_tools
    )


async def get_weibo_trending_func() -> list:
    """获取微博热搜榜数据"""
    # 使用微博移动端API，比PC端API更稳定
    url = "https://m.weibo.cn/api/container/getIndex?containerid=106003type%3D25%26t%3D3%26disable_hot%3D1%26filter_type%3Drealtimehot&title=%E5%BE%AE%E5%8D%9A%E7%83%AD%E6%90%9C&extparam=filter_type%3Drealtimehot%26mi_cid%3D100103%26pos%3D0_0%26c_type%3D30%26display_time%3D1540538388&luicode=10000011&lfid=231583"
    
    # 添加完整的请求头模拟移动端访问
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Referer": "https://s.weibo.com/top/summary?cate=realtimehot",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
        "mweibo-pwa": "1",
        "x-requested-with": "XMLHttpRequest",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin"
    }
    
    try:
        response = await http_client.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        if not data.get("data", {}).get("cards"):
            raise Exception("获取微博热搜榜失败")
        
        results = []
        # 获取热搜卡片数据
        cards = data["data"]["cards"]
        if not cards or not cards[0].get("card_group"):
            raise Exception("微博热搜数据格式异常")
        
        for item in cards[0]["card_group"]:
            # 跳过第一个元素（通常是标题）和广告内容
            if not item.get("desc") or item.get("actionlog", {}).get("ext", "").find("ads_word") != -1:
                continue
                
            # 构建搜索URL
            search_key = f"#{item['desc']}#"
            params = {
                "q": search_key,
                "band_rank": "1",
                "Refer": "top"
            }
            link = f"https://s.weibo.com/weibo?{urlencode(params)}"
            
            results.append({
                "title": item["desc"],
                "description": item["desc"],
                "popularity": "",  # 移动端API不直接提供热度值
                "link": link,
            })
        
        return results
        
    except Exception as e:
        # 如果移动端API失败，尝试使用备用方案
        print(f"移动端API失败: {e}")
        return await get_weibo_trending_fallback()


async def get_weibo_trending_fallback() -> list:
    """备用方案：使用简化的移动端API"""
    try:
        # 使用更简单的移动端API
        url = "https://m.weibo.cn/api/container/getIndex?containerid=106003type=25&t=3&disable_hot=1&filter_type=realtimehot"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
            "Referer": "https://m.weibo.cn/",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }
        
        response = await http_client.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        if not data.get("data", {}).get("cards"):
            raise Exception("备用API也失败了")
        
        results = []
        cards = data["data"]["cards"]
        if cards and cards[0].get("card_group"):
            for item in cards[0]["card_group"]:
                if item.get("desc"):
                    search_key = f"#{item['desc']}#"
                    params = {"q": search_key}
                    link = f"https://s.weibo.com/weibo?{urlencode(params)}"
                    
                    results.append({
                        "title": item["desc"],
                        "description": item["desc"],
                        "popularity": "",
                        "link": link,
                    })
        
        return results
        
    except Exception as e:
        print(f"备用API也失败: {e}")
        # 返回空结果而不是抛出异常
        return []


weibo_tool_config = Tool.from_function(
    fn=get_weibo_trending_func,
    name="get-weibo-trending",
    description="获取微博热搜榜，包含时事热点、社会现象、娱乐新闻、明星动态及网络热议话题的实时热门中文资讯",
)

# 整合所有微博工具
weibo_hot_tools = [
    weibo_tool_config,
    *weibo_search_tools,
    *weibo_user_tools,
    *weibo_comments_tools,
]

def main():
    result = asyncio.run(get_weibo_trending_func())
    print(f"结果是：{result}")

if __name__ == "__main__":
    main()
