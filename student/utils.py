from .models import Ranking, Experience


def ranking(instance):
    rank = None
    points = Ranking.objects.filter(
        domain=instance.domain
    ).values_list('domain__experience__points', flat=True).distinct().order_by('-domain__experience__points')

    new_point = Experience.objects.get(student=instance.student, domain=instance.domain).points

    for i in range(len(points)):
        if new_point == int(points[i]):
            rank = i + 1
            break

    instance.rank = rank
    instance.save()

    rest_exps = Experience.objects.filter(points__lt=new_point, domain=instance.domain)

    for rest_exp in rest_exps:
        rest_rank = Ranking.objects.get(student=rest_exp.student, domain=instance.domain)
        rest_rank.rank = rest_rank.rank + 1
        rest_rank.save()
