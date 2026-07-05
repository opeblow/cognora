import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { contentService, type TopicProgress } from "@/services/contentService"

export function useTopicProgress(topicId: string, totalSections: number = 0) {
  const queryClient = useQueryClient()

  const { data: progress, isLoading } = useQuery({
    queryKey: ["topic-progress", topicId],
    queryFn: () => contentService.getTopicProgress(topicId),
    staleTime: 30_000,
  })

  const updateProgress = useMutation({
    mutationFn: (update: Partial<TopicProgress>) =>
      contentService.updateTopicProgress(topicId, update),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["topic-progress", topicId] })
    },
  })

  const sectionsRead = progress?.sections_read?.length ?? 0
  const total = progress?.total_sections ?? totalSections

  return {
    progress,
    isLoading,
    sectionsRead,
    totalSections: total,
    progressPercent: total > 0 ? Math.round((sectionsRead / total) * 100) : 0,
    exerciseAccuracy:
      (progress?.exercises_attempted ?? 0) > 0
        ? Math.round(
            ((progress?.exercises_passed ?? 0) /
              (progress?.exercises_attempted ?? 1)) *
              100
          )
        : 0,
    display: `${sectionsRead} of ${total}`,
    deepDivesCompleted: progress?.deep_dives_completed?.length ?? 0,
    markSectionRead: (sectionIndex: number) => {
      const current = progress?.sections_read ?? []
      if (!current.includes(sectionIndex)) {
        updateProgress.mutate({
          sections_read: [...current, sectionIndex],
          total_sections: total,
        })
      }
    },
    markExerciseComplete: (passed: boolean) => {
      updateProgress.mutate({
        exercises_attempted: (progress?.exercises_attempted ?? 0) + 1,
        exercises_passed:
          (progress?.exercises_passed ?? 0) + (passed ? 1 : 0),
      })
    },
    savePosition: (scrollPercent: string) => {
      updateProgress.mutate({ last_position: scrollPercent })
    },
  }
}
