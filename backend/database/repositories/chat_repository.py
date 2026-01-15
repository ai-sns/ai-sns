"""Chat repository with specialized CRUD operations."""
from typing import List, Optional
from datetime import datetime
from sqlalchemy import desc, asc, or_
from .base import BaseRepository
from ..models.chat import AIChatMessages, AIFriend, AIChatInform, AiChatCfg, HumanChatCfg
from backend.config.database import get_db_session as get_session


class AIChatMessagesRepository(BaseRepository[AIChatMessages]):
    """AI chat messages repository."""

    def __init__(self):
        super().__init__(AIChatMessages)

    def get_previous_messages(self, last_record_id: Optional[int] = None, count: int = 20, **kwargs) -> List[AIChatMessages]:
        """Get previous messages with pagination."""
        session = get_session()
        try:
            query = session.query(self.model)
            if last_record_id is not None:
                query = query.filter(AIChatMessages.id < last_record_id)
            return query.filter_by(**kwargs).order_by(desc(AIChatMessages.create_time)).limit(count).all()
        finally:
            session.close()

    def get_all_ordered(self, label: bool = False, **kwargs) -> List[AIChatMessages]:
        """Get all messages ordered by stick time and create time."""
        session = get_session()
        try:
            query = session.query(self.model)
            if label:
                query = query.filter(AIChatMessages.label.isnot(None))

            return query.filter_by(**kwargs).order_by(
                desc(AIChatMessages.stick_time), desc(AIChatMessages.create_time)
            ).limit(20).all()
        finally:
            session.close()

    def get_labels(self, is_first: bool, owner_account: str, friend_account: str) -> List[str]:
        """Get distinct labels."""
        session = get_session()
        try:
            res = session.query(AIChatMessages.label).filter(
                AIChatMessages.is_first == True,
                AIChatMessages.owner_account == owner_account,
                AIChatMessages.friend_account == friend_account
            ).distinct().all()
            return [i.label for i in res if i.label is not None]
        finally:
            session.close()

    def search_content(self, label: bool = False, **kwargs) -> List[AIChatMessages]:
        """Search messages by title or content."""
        session = get_session()
        try:
            is_first = kwargs.get('is_first')
            owner_account = kwargs.get('owner_account')
            friend_account = kwargs.get('friend_account')
            title_keyword = kwargs.get('title')
            content_keyword = kwargs.get('content')

            query = session.query(self.model)

            if is_first is not None:
                query = query.filter(AIChatMessages.is_first == is_first)
            if owner_account is not None:
                query = query.filter(AIChatMessages.owner_account == owner_account)
            if friend_account is not None:
                query = query.filter(AIChatMessages.friend_account == friend_account)
            if title_keyword == "":
                query = query.filter(AIChatMessages.is_first == True)
            if label:
                query = query.filter(AIChatMessages.label.isnot(None))

            search_terms = []
            if title_keyword:
                search_terms.append(AIChatMessages.title.contains(title_keyword))
            if content_keyword:
                search_terms.append(AIChatMessages.content.contains(content_keyword))

            if search_terms:
                query = query.filter(or_(*search_terms))

            return query.order_by(desc(AIChatMessages.stick_time), desc(AIChatMessages.create_time)).limit(50000).all()
        finally:
            session.close()

    def get_conversation_content(self, id: int) -> List[AIChatMessages]:
        """Get full conversation content by first message ID."""
        session = get_session()
        try:
            first_msg = session.query(self.model).filter(
                AIChatMessages.is_first == True, AIChatMessages.id == id
            ).one_or_none()

            if not first_msg:
                return []

            return session.query(self.model).filter(
                AIChatMessages.conversation_id == first_msg.conversation_id
            ).order_by(asc(AIChatMessages.create_time)).all()
        finally:
            session.close()

    def update_stick_time(self, id: int, value: Optional[datetime] = None):
        """Update stick time."""
        self.update(id, stick_time=value)


class AIFriendRepository(BaseRepository[AIFriend]):
    """AI friend repository."""

    def __init__(self):
        super().__init__(AIFriend)

    def get_all_ordered_by_update_time(self, **kwargs) -> List[AIFriend]:
        """Get all friends ordered by last message time."""
        session = get_session()
        try:
            return session.query(self.model).filter_by(**kwargs).order_by(desc(AIFriend.last_message_time)).all()
        finally:
            session.close()

    def update_by_account(self, account: str, owner_sns_account: str, **kwargs):
        """Update friend by account and owner."""
        filters = {'account': account, 'owner_sns_account': owner_sns_account}
        self.update_by_filter(filters, **kwargs)


class AIChatInformRepository(BaseRepository[AIChatInform]):
    """AI chat notification repository."""

    def __init__(self):
        super().__init__(AIChatInform)


class AiChatCfgRepository(BaseRepository[AiChatCfg]):
    """AI chat configuration repository."""

    def __init__(self):
        super().__init__(AiChatCfg)

    def create_with_id(self, **kwargs) -> int:
        """Create configuration and return its ID."""
        session = get_session()
        try:
            cfg = self.model(**kwargs)
            session.add(cfg)
            session.flush()
            record_id = cfg.id
            session.refresh(cfg)
            session.commit()
            return record_id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_all_ordered(self, **kwargs) -> List[AiChatCfg]:
        """Get all configurations ordered by position."""
        session = get_session()
        try:
            return session.query(self.model).filter_by(**kwargs).order_by(asc(AiChatCfg.position)).all()
        finally:
            session.close()

    def search_content(self, **kwargs) -> List[AiChatCfg]:
        """Search configurations by nickname or account."""
        session = get_session()
        try:
            nickname_keyword = kwargs.get('nickname')
            account_keyword = kwargs.get('account')

            query = session.query(self.model)

            search_terms = []
            if nickname_keyword:
                search_terms.append(AiChatCfg.nickname.contains(nickname_keyword))
            if account_keyword:
                search_terms.append(AiChatCfg.account.contains(account_keyword))

            if search_terms:
                query = query.filter(or_(*search_terms))

            return query.order_by(desc(AiChatCfg.create_time)).limit(50000).all()
        finally:
            session.close()

    def get_map_config(self) -> Optional[AiChatCfg]:
        """Get first map configuration."""
        session = get_session()
        try:
            return session.query(self.model).first()
        finally:
            session.close()

    def get_common_config(self) -> Optional[AiChatCfg]:
        """Get common configuration (second record)."""
        session = get_session()
        try:
            return session.query(self.model).offset(1).limit(1).first()
        finally:
            session.close()

    def get_map_settings(self, **kwargs) -> Optional[dict]:
        """Get map settings as dictionary."""
        session = get_session()
        try:
            record = session.query(self.model).filter_by(**kwargs).first()
            if record:
                return {
                    "nick_name": record.nickname,
                    "account": record.account,
                    "profile": record.sign,
                    "profession": record.profession,
                    "nationid": record.nationid,
                    "nationpassword": record.nationpassword,
                    "sns_url": record.sns_url,
                    "status": record.status,
                    "avatar": record.avatar,
                    "avatar3d": record.avatar3d,
                    "house3d": record.house3d,
                    "map_type": record.map_type,
                    "map_api_key": record.map_api_key,
                    "map_id": record.map_id,
                    "current_position": record.current_position,
                    "home_position": record.home_position,
                    "positionx": record.positionx,
                    "positiony": record.positiony,
                    "positionz": record.positionz,
                    "route_start": record.route_start,
                    "route_end": record.route_end,
                    "route_status": record.route_status,
                    "route_current_position": record.route_current_position,
                    "route": record.route
                }
            return None
        finally:
            session.close()

    def update_map_config(self, **kwargs):
        """Update first map configuration."""
        session = get_session()
        try:
            record = session.query(self.model).first()
            if record:
                for key, value in kwargs.items():
                    setattr(record, key, value)
                session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


class HumanChatCfgRepository(BaseRepository[HumanChatCfg]):
    """Human chat configuration repository."""

    def __init__(self):
        super().__init__(HumanChatCfg)
