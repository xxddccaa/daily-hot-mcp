"""微博搜索工具"""

import asyncio
import random
import time
from urllib.parse import urlencode
from daily_hot_mcp.utils import http_client
from fastmcp.tools import Tool


async def search_weibo_content(keyword: str, limit: int = 15, page: int = 1) -> list:
    """搜索微博内容"""
    try:
        # 添加随机延迟避免被检测
        await asyncio.sleep(random.uniform(1, 3))
        
        # 使用微博移动端搜索API
        params = {
            'containerid': f'100103type=1&q={keyword}',
            'page_type': 'searchall',
            'page': page,
        }
        encoded_params = urlencode(params)
        url = f"https://m.weibo.cn/api/container/getIndex?{encoded_params}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Referer": "https://s.weibo.com/",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "mweibo-pwa": "1",
            "x-requested-with": "XMLHttpRequest",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
        }
        
        # 重试机制
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await http_client.get(url, headers=headers)
                response.raise_for_status()
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                await asyncio.sleep(random.uniform(2, 5))
        
        data = response.json()
        if not data.get("data", {}).get("cards"):
            return []
        
        results = []
        cards = data["data"]["cards"]
        
        for card in cards:
            if card.get('card_type') == 9:  # 微博内容卡片
                mblog = card.get('mblog')
                if mblog:
                    user = mblog.get('user', {})
                    results.append({
                        "id": mblog.get('id'),
                        "text": mblog.get('text', ''),
                        "created_at": mblog.get('created_at', ''),
                        "user": {
                            "id": user.get('id'),
                            "screen_name": user.get('screen_name', ''),
                            "profile_image_url": user.get('profile_image_url', ''),
                        },
                        "comments_count": mblog.get('comments_count', 0),
                        "attitudes_count": mblog.get('attitudes_count', 0),
                        "reposts_count": mblog.get('reposts_count', 0),
                        "url": f"https://m.weibo.cn/status/{mblog.get('id')}",
                    })
            elif 'card_group' in card and isinstance(card['card_group'], list):
                for item in card['card_group']:
                    if item.get('card_type') == 9:
                        mblog = item.get('mblog')
                        if mblog:
                            user = mblog.get('user', {})
                            results.append({
                                "id": mblog.get('id'),
                                "text": mblog.get('text', ''),
                                "created_at": mblog.get('created_at', ''),
                                "user": {
                                    "id": user.get('id'),
                                    "screen_name": user.get('screen_name', ''),
                                    "profile_image_url": user.get('profile_image_url', ''),
                                },
                                "comments_count": mblog.get('comments_count', 0),
                                "attitudes_count": mblog.get('attitudes_count', 0),
                                "reposts_count": mblog.get('reposts_count', 0),
                                "url": f"https://m.weibo.cn/status/{mblog.get('id')}",
                            })
            
            if len(results) >= limit:
                break
        
        return results[:limit]
        
    except Exception as e:
        print(f"搜索微博内容失败: {e}")
        return []


async def search_weibo_topics(keyword: str, limit: int = 15, page: int = 1) -> list:
    """搜索微博话题"""
    try:
        # 添加随机延迟避免被检测
        await asyncio.sleep(random.uniform(1, 3))
        
        params = {
            'containerid': f'100103type=38&q={keyword}',
            'page_type': 'searchall',
            'page': page,
        }
        encoded_params = urlencode(params)
        url = f"https://m.weibo.cn/api/container/getIndex?{encoded_params}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Referer": "https://s.weibo.com/",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "mweibo-pwa": "1",
            "x-requested-with": "XMLHttpRequest",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
        }
        
        # 重试机制
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await http_client.get(url, headers=headers)
                response.raise_for_status()
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                await asyncio.sleep(random.uniform(2, 5))
        
        data = response.json()
        if not data.get("data", {}).get("cards"):
            return []
        
        results = []
        cards = data["data"]["cards"]
        
        if cards and cards[0].get('card_group'):
            for item in cards[0]['card_group'][:limit]:
                results.append({
                    "title": item.get('title_sub', ''),
                    "desc1": item.get('desc1', ''),
                    "desc2": item.get('desc2', ''),
                    "url": item.get('scheme', ''),
                })
        
        return results
        
    except Exception as e:
        print(f"搜索微博话题失败: {e}")
        return []


async def search_weibo_users(keyword: str, limit: int = 15, page: int = 1) -> list:
    """搜索微博用户"""
    try:
        # 添加随机延迟避免被检测
        await asyncio.sleep(random.uniform(1, 3))
        
        params = {
            'containerid': f'100103type=3&q={keyword}',
            'page_type': 'searchall',
            'page': page,
        }
        encoded_params = urlencode(params)
        url = f"https://m.weibo.cn/api/container/getIndex?{encoded_params}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Referer": "https://s.weibo.com/",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "mweibo-pwa": "1",
            "x-requested-with": "XMLHttpRequest",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
        }
        
        # 重试机制
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await http_client.get(url, headers=headers)
                response.raise_for_status()
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                await asyncio.sleep(random.uniform(2, 5))
        
        data = response.json()
        if not data.get("data", {}).get("cards"):
            return []
        
        results = []
        cards = data["data"]["cards"]
        
        if len(cards) >= 2 and cards[1].get('card_group'):
            for item in cards[1]['card_group'][:limit]:
                user = item.get('user', {})
                results.append({
                    "id": user.get('id'),
                    "screen_name": user.get('screen_name', ''),
                    "profile_image_url": user.get('profile_image_url', ''),
                    "profile_url": user.get('profile_url', ''),
                    "description": user.get('description', ''),
                    "follow_count": user.get('follow_count', 0),
                    "followers_count": user.get('followers_count', ''),
                    "verified": user.get('verified', False),
                    "verified_reason": user.get('verified_reason', ''),
                })
        
        return results
        
    except Exception as e:
        print(f"搜索微博用户失败: {e}")
        return []


# 创建工具配置
weibo_search_content_tool = Tool.from_function(
    fn=search_weibo_content,
    name="search-weibo-content",
    description="搜索微博内容，根据关键词查找相关微博动态",
)

weibo_search_topics_tool = Tool.from_function(
    fn=search_weibo_topics,
    name="search-weibo-topics",
    description="搜索微博话题，根据关键词查找相关话题",
)

weibo_search_users_tool = Tool.from_function(
    fn=search_weibo_users,
    name="search-weibo-users",
    description="搜索微博用户，根据关键词查找相关用户",
)

weibo_search_tools = [
    weibo_search_content_tool,
    weibo_search_topics_tool,
    weibo_search_users_tool,
]


def main():
    """测试函数"""
    async def test():
        # 测试搜索内容
        print("=== 测试搜索微博内容 ===")
        content_results = await search_weibo_content("人工智能", limit=3)
        for item in content_results:
            print(f"内容: {item['text'][:50]}...")
            print(f"用户: {item['user']['screen_name']}")
            print(f"点赞: {item['attitudes_count']}")
            print("---")
        
        # 测试搜索话题
        print("\n=== 测试搜索微博话题 ===")
        topic_results = await search_weibo_topics("人工智能", limit=3)
        for item in topic_results:
            print(f"话题: {item['title']}")
            print(f"描述: {item['desc2']}")
            print("---")
        
        # 测试搜索用户
        print("\n=== 测试搜索微博用户 ===")
        user_results = await search_weibo_users("雷军", limit=3)
        for item in user_results:
            print(f"用户: {item['screen_name']}")
            print(f"粉丝: {item['followers_count']}")
            print(f"认证: {item['verified_reason']}")
            print("---")
    
    asyncio.run(test())


if __name__ == "__main__":
    main()
