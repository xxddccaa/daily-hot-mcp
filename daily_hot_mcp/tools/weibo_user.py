"""微博用户信息工具"""

import asyncio
from urllib.parse import urlencode
from daily_hot_mcp.utils import http_client
from fastmcp.tools import Tool


async def get_weibo_user_profile(uid: int) -> dict:
    """获取微博用户详细信息"""
    try:
        url = f"https://m.weibo.cn/api/container/getIndex?type=uid&value={uid}"
        
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
        if not data.get("data", {}).get("userInfo"):
            return {}
        
        user_info = data["data"]["userInfo"]
        
        return {
            "id": user_info.get('id'),
            "screen_name": user_info.get('screen_name', ''),
            "profile_image_url": user_info.get('profile_image_url', ''),
            "profile_url": user_info.get('profile_url', ''),
            "description": user_info.get('description', ''),
            "follow_count": user_info.get('follow_count', 0),
            "followers_count": user_info.get('followers_count', ''),
            "avatar_hd": user_info.get('avatar_hd', ''),
            "verified": user_info.get('verified', False),
            "verified_reason": user_info.get('verified_reason', ''),
            "gender": user_info.get('gender', ''),
        }
        
    except Exception as e:
        print(f"获取用户信息失败: {e}")
        return {}


async def get_weibo_user_feeds(uid: int, limit: int = 15) -> list:
    """获取用户微博动态"""
    try:
        # 首先获取container_id
        profile_url = f"https://m.weibo.cn/api/container/getIndex?type=uid&value={uid}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
            "Referer": "https://m.weibo.cn/",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "mweibo-pwa": "1",
            "x-requested-with": "XMLHttpRequest",
        }
        
        # 获取用户信息以获取container_id
        profile_response = await http_client.get(profile_url, headers=headers)
        profile_response.raise_for_status()
        profile_data = profile_response.json()
        
        tabs_info = profile_data.get("data", {}).get("tabsInfo", {}).get("tabs", [])
        container_id = None
        for tab in tabs_info:
            if tab.get("tabKey") == "weibo":
                container_id = tab.get("containerid")
                break
        
        if not container_id:
            return []
        
        # 获取用户动态
        feeds_url = f"https://m.weibo.cn/api/container/getIndex?type=uid&value={uid}&containerid={container_id}&since_id=0"
        
        response = await http_client.get(feeds_url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        if not data.get("data", {}).get("cards"):
            return []
        
        results = []
        cards = data["data"]["cards"]
        
        for card in cards:
            if card.get('mblog'):
                mblog = card['mblog']
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
                
                if len(results) >= limit:
                    break
        
        return results[:limit]
        
    except Exception as e:
        print(f"获取用户动态失败: {e}")
        return []


async def get_weibo_user_followers(uid: int, limit: int = 15, page: int = 1) -> list:
    """获取用户关注列表"""
    try:
        params = {
            'containerid': f'231051_-_followers_-_{uid}',
            'page': page,
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
        
        if cards and cards[-1].get('card_group'):
            for item in cards[-1]['card_group'][:limit]:
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
        print(f"获取关注列表失败: {e}")
        return []


async def get_weibo_user_fans(uid: int, limit: int = 15, page: int = 1) -> list:
    """获取用户粉丝列表"""
    try:
        params = {
            'containerid': f'231051_-_fans_-_{uid}',
            'page': page,
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
        
        if cards and cards[-1].get('card_group'):
            for item in cards[-1]['card_group'][:limit]:
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
        print(f"获取粉丝列表失败: {e}")
        return []


# 创建工具配置
weibo_user_profile_tool = Tool.from_function(
    fn=get_weibo_user_profile,
    name="get-weibo-user-profile",
    description="获取微博用户详细信息，包括认证状态、粉丝数等",
)

weibo_user_feeds_tool = Tool.from_function(
    fn=get_weibo_user_feeds,
    name="get-weibo-user-feeds",
    description="获取微博用户的动态内容，包括最新发布的微博",
)

weibo_user_followers_tool = Tool.from_function(
    fn=get_weibo_user_followers,
    name="get-weibo-user-followers",
    description="获取微博用户的关注列表",
)

weibo_user_fans_tool = Tool.from_function(
    fn=get_weibo_user_fans,
    name="get-weibo-user-fans",
    description="获取微博用户的粉丝列表",
)

weibo_user_tools = [
    weibo_user_profile_tool,
    weibo_user_feeds_tool,
    weibo_user_followers_tool,
    weibo_user_fans_tool,
]


def main():
    """测试函数"""
    async def test():
        # 测试获取用户信息（雷军的UID）
        print("=== 测试获取用户信息 ===")
        profile = await get_weibo_user_profile(1749127163)
        if profile:
            print(f"用户名: {profile['screen_name']}")
            print(f"粉丝数: {profile['followers_count']}")
            print(f"认证: {profile['verified_reason']}")
            print("---")
        
        # 测试获取用户动态
        print("\n=== 测试获取用户动态 ===")
        feeds = await get_weibo_user_feeds(1749127163, limit=2)
        for feed in feeds:
            print(f"内容: {feed['text'][:50]}...")
            print(f"点赞: {feed['attitudes_count']}")
            print("---")
    
    asyncio.run(test())


if __name__ == "__main__":
    main()
