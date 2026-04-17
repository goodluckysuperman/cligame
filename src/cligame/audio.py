from __future__ import annotations

import platform
import subprocess
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Protocol


class AudioPlayer(Protocol):
    def start_bgm(self, track_name: str) -> None: ...

    def play_ending(self, track_name: str) -> None: ...

    def stop_bgm(self) -> None: ...


@dataclass
class NoopAudioPlayer:
    enabled: bool = True
    current_track: str | None = None

    def start_bgm(self, track_name: str) -> None:
        if not self.enabled:
            return
        self.current_track = track_name

    def play_ending(self, track_name: str) -> None:
        if not self.enabled:
            return
        self.current_track = track_name

    def stop_bgm(self) -> None:
        self.current_track = None


@dataclass
class WindowsAudioPlayer:
    enabled: bool = True
    current_process: subprocess.Popen[str] | None = None
    current_track: str | None = None

    def start_bgm(self, track_name: str) -> None:
        if not self.enabled:
            return
        self.stop_bgm()
        self.current_process = self._spawn_player(track_name, loop=True)
        self.current_track = track_name

    def play_ending(self, track_name: str) -> None:
        if not self.enabled:
            return
        self.stop_bgm()
        self.current_process = self._spawn_player(track_name, loop=False)
        self.current_track = track_name

    def stop_bgm(self) -> None:
        if self.current_process and self.current_process.poll() is None:
            self.current_process.terminate()
            try:
                self.current_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.current_process.kill()
        self.current_process = None
        self.current_track = None

    def _spawn_player(self, track_name: str, loop: bool) -> subprocess.Popen[str]:
        asset_path = resolve_audio_asset(track_name)
        if loop:
            script = (
                "$p = Resolve-Path '" + str(asset_path).replace("'", "''") + "'; "
                "Add-Type -AssemblyName PresentationCore; "
                "$player = New-Object System.Windows.Media.MediaPlayer; "
                "$player.Open([Uri]$p.Path); "
                "Start-Sleep -Milliseconds 1200; "
                "$duration = if ($player.NaturalDuration.HasTimeSpan) { $player.NaturalDuration.TimeSpan.TotalSeconds } else { 10 }; "
                "$player.Play(); "
                "while ($true) { Start-Sleep -Milliseconds ([Math]::Max(500, [int](($duration - 0.5) * 1000))); $player.Stop(); $player.Position = [TimeSpan]::Zero; $player.Play() }"
            )
        else:
            script = (
                "$p = Resolve-Path '" + str(asset_path).replace("'", "''") + "'; "
                "Add-Type -AssemblyName PresentationCore; "
                "$player = New-Object System.Windows.Media.MediaPlayer; "
                "$player.Open([Uri]$p.Path); "
                "$player.Play(); "
                "while ($true) { Start-Sleep -Seconds 1 }"
            )
        return subprocess.Popen([
            "powershell.exe",
            "-NoProfile",
            "-Command",
            script,
        ])


def resolve_audio_asset(track_name: str) -> Path:
    return Path(resources.files("cligame.content.audio").joinpath(track_name))


def create_audio_player(enabled: bool) -> AudioPlayer:
    if not enabled:
        return NoopAudioPlayer(enabled=False)
    if platform.system() == "Windows":
        return WindowsAudioPlayer(enabled=True)
    return NoopAudioPlayer(enabled=True)
