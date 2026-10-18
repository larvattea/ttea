"""Factory of the KarTEA register screens (views + controllers).

Attributes
----------
EditViewFactory : type
    Type of a callable that builds the edit screen:
    ``(parent, config) -> PlayerKarteaConfigEditView``.
"""

import inspect
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QDialog

from ttea.factory.gameviewfactoryprotocol import GameViewFactoryProtocol
from ttea.games.kartea.controller import (
    PlayerKarteaConfigEditController,
    PlayerKarteaConfigListController,
)
from ttea.games.kartea.service import (
    KarteaPhaseService,
    PlayerKarteaConfigService,
)
from ttea.games.kartea.view import (
    PlayerKarteaConfigEditView,
    PlayerKarteaConfigListView,
)

if TYPE_CHECKING:
    from ttea.games.kartea.model import PlayerKarteaConfig


EditViewFactory = Callable[
    [QDialog | None, "PlayerKarteaConfig | None"],
    PlayerKarteaConfigEditView,
]


def _supported_kwargs(
    factory: Callable, kwargs: dict[str, Any]
) -> dict[str, Any]:
    """Return only the keyword arguments the factory accepts.

    Parameters
    ----------
    factory : Callable
        Function whose signature is inspected.
    kwargs : dict[str, Any]
        Candidate keyword arguments.

    Returns
    -------
    dict[str, Any]
        All ``kwargs`` if the factory takes ``**kwargs``; otherwise only
        those named in its signature. Empty if the signature cannot be
        inspected.

    Examples
    --------
    >>> def make(parent, config, service=None):
    ...     pass
    >>> _supported_kwargs(make, {"service": 1, "phase_service": 2})
    {'service': 1}
    """
    try:
        params = inspect.signature(factory).parameters.values()
    except (TypeError, ValueError):
        return {}
    if any(p.kind is inspect.Parameter.VAR_KEYWORD for p in params):
        return kwargs
    names = {p.name for p in params}
    return {k: v for k, v in kwargs.items() if k in names}


class KarteaViewFactory(GameViewFactoryProtocol):
    """Build the KarTEA register screens.

    For each screen, create the view, create the controller with the
    services and connect both (``view.bind(controller)``). Views and
    controllers neither create each other nor create services.

    Notes
    -----
    Each list screen receives ONE instance of each service, shared with
    the edit dialogs opened from it. The instances are deliberately not
    global: the game runs in another process and writes the same CSV
    files (phase/level, session); a list opened after a match must read
    the data again, not an old cache.
    """

    @staticmethod
    def create_player_config_edit_view(
        parent: QDialog | None = None,
        config: "PlayerKarteaConfig | None" = None,
        service: PlayerKarteaConfigService | None = None,
        phase_service: KarteaPhaseService | None = None,
    ) -> PlayerKarteaConfigEditView:
        """Create the player configuration edit screen.

        Parameters
        ----------
        parent : QDialog | None, optional
            Parent widget of the dialog.
        config : PlayerKarteaConfig | None, optional
            Config to edit; None opens the screen to create a new one.
        service : PlayerKarteaConfigService | None, optional
            Config service to share (e.g. the list screen's). Created if
            None.
        phase_service : KarteaPhaseService | None, optional
            Phase service to share. Created if None.

        Returns
        -------
        PlayerKarteaConfigEditView
            The view, already bound to its controller.

        Notes
        -----
        Without services (dialog opened outside the list), the screen
        creates its own.
        """
        service = service or PlayerKarteaConfigService()
        phase_service = phase_service or KarteaPhaseService()

        view = PlayerKarteaConfigEditView(parent, editing=config is not None)
        controller = PlayerKarteaConfigEditController(
            view, config, service, phase_service
        )
        view.bind(controller)
        return view

    @staticmethod
    def create_player_config_list_view(
        parent: QObject | None = None,
        player_config_edit_view: EditViewFactory | None = None,
    ) -> PlayerKarteaConfigListView:
        """Create the player configuration list screen.

        Parameters
        ----------
        parent : QObject | None, optional
            Parent of the view.
        player_config_edit_view : EditViewFactory | None, optional
            Factory of the edit dialog. Defaults to
            ``create_player_config_edit_view``.

        Returns
        -------
        PlayerKarteaConfigListView
            The view, already bound to its controller.

        Notes
        -----
        Creates one PlayerKarteaConfigService and one KarteaPhaseService
        and shares them with every edit dialog opened from the list.
        They are passed only as the keyword arguments the edit factory
        accepts, so a factory with the plain ``(parent, config)``
        signature also works.
        """
        service = PlayerKarteaConfigService()
        phase_service = KarteaPhaseService()
        edit_factory = (
            player_config_edit_view
            or KarteaViewFactory.create_player_config_edit_view
        )
        shared = _supported_kwargs(
            edit_factory, {"service": service, "phase_service": phase_service}
        )

        def bound_edit_factory(
            edit_parent: QDialog | None = None,
            config: "PlayerKarteaConfig | None" = None,
        ) -> PlayerKarteaConfigEditView:
            """Open the edit dialog with the list's shared services."""
            return edit_factory(edit_parent, config, **shared)

        view = PlayerKarteaConfigListView(parent)
        controller = PlayerKarteaConfigListController(
            view, bound_edit_factory, service
        )
        view.bind(controller)
        return view
