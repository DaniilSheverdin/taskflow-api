from typing import Optional

from app.dao.base import BaseDAO
from app.models.refresh_session import RefreshSession
from app.schemas.token import TokenSession


class RefreshSessionDAO(BaseDAO):
    model = RefreshSession

    async def get_session_by_refresh_token(
        self, refresh_token: str
    ) -> Optional[RefreshSession]:
        return await self.find_one_or_none(
            filter_dict={"refresh_token": refresh_token},
            order_by_field="created_at",
            order_desc=True,
        )

    async def delete_session(self, session: RefreshSession):
        await self._session.delete(session)
        await self._session.commit()

    async def delete_all_user_sessions(self, user_id: int):
        """
        Удаляем все сессии пользователя
        :param user_id:
        :return:
        """
        all_sessions = await self.find(filter_dict={"user_id": user_id})
        for session in all_sessions:
            await self._session.delete(session)
        await self._session.commit()

    async def delete_last_session_for_token(self, token: str):
        session = await self.get_session_by_refresh_token(token)
        if not session:
            return
        await self._session.delete(session)
        await self._session.commit()

    async def check_old_sessions(self, user_id: int, max_sessions: int) -> bool:
        """
        Проверяет наличие старых сессий пользователя сверх указанного в числа. Удаляет самые старые сессии сверх указанного числа.
        :param max_sessions:
        :param user_id:
        :return:
        """
        over_max_sessions = False
        all_sessions = await self.find(filter_dict={"user_id": user_id})
        if all_sessions is not None and len(all_sessions) > max_sessions - 1:
            over_max_sessions = True
            all_sessions.sort(key=lambda s: s.created_at)
            for old_session in all_sessions[: -max_sessions + 1]:
                await self._session.delete(old_session)
            await self._session.commit()

        return over_max_sessions

    async def create_session(self, data: TokenSession, max_sessions: int):
        """
        Создает новую сессию. Удаляет сессии сверх указанного числа
        :param data:
        :param max_sessions:
        :return:
        """
        await self.check_old_sessions(data.user_id, max_sessions)

        await super().create(data=data)
        await self._session.commit()
