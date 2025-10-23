"""微博评论工具"""

import asyncio
from urllib.parse import urlencode
from daily_hot_mcp.utils import http_client
from fastmcp.tools import Tool


async def get_weibo_comments(feed_id: str, page: int = 1, limit: int = 20) -> list:
    """获取微博评论"""
    try:
        url = f"https://m.weibo.cn/api/comments/show?id={feed_id}&page={page}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
            "Referer": f"https://m.weibo.cn/status/{feed_id}",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "mweibo-pwa": "1",
            "x-requested-with": "XMLHttpRequest",
        }
        
        response = await http_client.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        if not data.get("data", {}).get("data"):
            return []
        
        results = []
        comments = data["data"]["data"]
        
        for comment in comments[:limit]:
            user = comment.get('user', {})
            results.append({
                "id": comment.get('id'),
                "text": comment.get('text', ''),
                "created_at": comment.get('created_at', ''),
                "source": comment.get('source', ''),
                "user": {
                    "id": user.get('id'),
                    "screen_name": user.get('screen_name', ''),
                    "profile_image_url": user.get('profile_image_url', ''),
                    "verified": user.get('verified', False),
                    "verified_reason": user.get('verified_reason', ''),
                },
                "reply_id": comment.get('reply_id'),
                "reply_text": comment.get('reply_text', ''),
                "like_count": comment.get('like_count', 0),
            })
        
        return results
        
    except Exception as e:
        print(f"获取微博评论失败: {e}")
        return []


async def get_weibo_hot_feeds(uid: int, limit: int = 15) -> list:
    """获取用户热门微博"""
    try:
        params = {
            'containerid': f'231002{uid}_-_HOTMBLOG',
            'type': 'uid',
            'value': uid,
        }
        encoded_params = urlencode(params)
        url = f"https://m.weibo.cn/api/container/getIndex?{encoded_params}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
            "Referer": "https://m.weibo.cn/",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "mweibo-pwa": "1",
            "x-requested-with": "XMLHttpRequest",
        }
        
        response = await http_client.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        if not data.get("data", {}).get("cards"):
            return []
        
        results = []
        cards = data["data"]["cards"]
        
        # 过滤出微博内容卡片
        content_cards = [card for card in cards if card.get('card_type') == 9]
        
        for card in content_cards[:limit]:
            mblog = card.get('mblog')
            if mblog:
                user = mblog.get('user', {})
                
                # 处理图片
                pics = []
                if mblog.get('pics'):
                    for pic in mblog['pics']:
                        if 'url' in pic:
                            pics.append({
                                'thumbnail': pic['url'],
                                'large': pic.get('large', {}).get('url', pic['url'])
                            })
                
                results.append({
                    "id": mblog.get('id'),
                    "text": mblog.get('text', ''),
                    "source": mblog.get('source', ''),
                    "created_at": mblog.get('created_at', ''),
                    "user": {
                        "id": user.get('id'),
                        "screen_name": user.get('screen_name', ''),
                        "profile_image_url": user.get('profile_image_url', ''),
                    },
                    "comments_count": mblog.get('comments_count', 0),
                    "attitudes_count": mblog.get('attitudes_count', 0),
                    "reposts_count": mblog.get('reposts_count', 0),
                    "pics": pics,
                    "url": f"https://m.weibo.cn/status/{mblog.get('id')}",
                })
        
        return results
        
    except Exception as e:
        print(f"获取热门微博失败: {e}")
        return []


# 创建工具配置
weibo_comments_tool = Tool.from_function(
    fn=get_weibo_comments,
    name="get-weibo-comments",
    description="获取微博评论，根据微博ID获取相关评论内容",
)

weibo_hot_feeds_tool = Tool.from_function(
    fn=get_weibo_hot_feeds,
    name="get-weibo-hot-feeds",
    description="获取用户热门微博，获取指定用户的热门动态内容",
)

weibo_comments_tools = [
    weibo_comments_tool,
    weibo_hot_feeds_tool,
]


def main():
    """测试函数"""
    async def test():
        # 测试获取评论（使用一个真实的微博ID）
        print("=== 测试获取微博评论 ===")
        comments = await get_weibo_comments("5167970394572058", limit=3)
        for comment in comments:
            print(f"用户: {comment['user']['screen_name']}")
            print(f"评论: {comment['text'][:50]}...")
            print(f"时间: {comment['created_at']}")
            print("---")
        
        # 测试获取热门微博
        print("\n=== 测试获取热门微博 ===")
        hot_feeds = await get_weibo_hot_feeds(1749127163, limit=2)
        for feed in hot_feeds:
            print(f"内容: {feed['text'][:50]}...")
            print(f"点赞: {feed['attitudes_count']}")
            print("---")
    
    asyncio.run(test())


if __name__ == "__main__":
    main()
