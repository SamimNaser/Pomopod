import { createElement, useEffect, useRef } from "react";
import { toast } from "sonner";

export type PomodoroSessionId = "focus" | "shortBreak" | "longBreak";

// Lower this during testing if you want the toast to appear sooner.
export const POMODORO_NOTIFICATION_TRIGGER_SECONDS = 50;

const sessionEndingCopy: Record<PomodoroSessionId, string> = {
  focus: "Focus ends in",
  shortBreak: "Short break ends in",
  longBreak: "Long break ends in",
};

type UsePomodoroEndingNotificationOptions = {
  activeSession: PomodoroSessionId;
  isRunning: boolean;
  timeLeft: number;
};

function PomodoroNotificationIndicator() {
  return createElement(
    "span",
    {
      className: "relative flex size-3 items-center justify-center",
    },
    createElement("span", {
      className: "absolute size-3 rounded-full bg-emerald-400/35 animate-ping",
    }),
    createElement("span", {
      className:
        "relative size-2.5 rounded-full bg-emerald-400 shadow-[0_0_12px_rgba(74,222,128,0.55)]",
    }),
  );
}

export function showPomodoroEndingNotification(session: PomodoroSessionId) {
  toast(
    `${sessionEndingCopy[session]} ${POMODORO_NOTIFICATION_TRIGGER_SECONDS}s`,
    {
      id: `pomodoro-ending-${session}`,
      duration: 2500,
      dismissible: true,
      icon: createElement(PomodoroNotificationIndicator),
    },
  );
}

export function usePomodoroEndingNotification({
  activeSession,
  isRunning,
  timeLeft,
}: UsePomodoroEndingNotificationOptions) {
  const notifiedSessionRef = useRef<PomodoroSessionId | null>(null);
  const triggerThresholdMs = POMODORO_NOTIFICATION_TRIGGER_SECONDS * 1000;

  useEffect(() => {
    if (timeLeft > triggerThresholdMs) {
      notifiedSessionRef.current = null;
    }
  }, [timeLeft, triggerThresholdMs]);

  useEffect(() => {
    if (!isRunning || timeLeft <= 0 || timeLeft > triggerThresholdMs) {
      return;
    }

    if (notifiedSessionRef.current === activeSession) {
      return;
    }

    showPomodoroEndingNotification(activeSession);

    notifiedSessionRef.current = activeSession;
  }, [activeSession, isRunning, timeLeft, triggerThresholdMs]);
}
