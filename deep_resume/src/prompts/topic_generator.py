import datetime
from .topic_model import Question, BackgroundInvestigation, Topic
from .resume_model import Resume, ExperienceType
from .report_model import QuestionType

# Chinese built-in questions
BUILT_IN_ACDEMIC_QUESTIONS_ZH_CN = [
    "%s在%s年是211吗？",
    "%s在%s年是985吗？",
    "%s在%s年 世界QS排名多少？",
    "%s在%s年 教育部公布的学科评估中 哪些专业为A+？"
]

BUILT_IN_PROFESSIONAL_QUESTIONS_ZH_CN = [
    "%s公司最主要收入来自于哪里？",
]

BUILT_IN_BACKGROUND_QUESTIONS_ZH_CN: dict[ExperienceType, str] = {
    ExperienceType.ACADEMIC: "%s简介",
    ExperienceType.PROFESSIONAL: "%s简介"
}

def generate_topic_list(resume: Resume) -> list[Topic]:
    res = []
    acdemic_description = []
    professional_description = []
    for experience in resume.experiences:
        if experience.experience_type == ExperienceType.ACADEMIC:
            acdemic_description.append(experience)
        elif experience.experience_type == ExperienceType.PROFESSIONAL:
            professional_description.append(experience)

    seen = set()
    acdemic_description = [x for x in acdemic_description if not (x.description in seen or seen.add(x.description))]
    seen = set()
    professional_description = [x for x in professional_description if not (x.description in seen or seen.add(x.description))]
    questions = []

    for acdemic in acdemic_description:
        for acdemic_question in BUILT_IN_ACDEMIC_QUESTIONS_ZH_CN:
            current_year = str(datetime.datetime.now().year)
            question = Question(
                description= acdemic_question % (acdemic.description, current_year),
                answered=False
            )
            questions.append(question)
        background_investigation = BackgroundInvestigation(
            background_search_description= BUILT_IN_BACKGROUND_QUESTIONS_ZH_CN[ExperienceType.ACADEMIC] % (acdemic.description),
            searched=False
        )
        topic = Topic(
            questions=questions,
            experience=acdemic,
            background_investigation=background_investigation
        )
        questions = []
        res.append(topic)

    questions = []
    for professional in professional_description:
        for professional_question in BUILT_IN_PROFESSIONAL_QUESTIONS_ZH_CN:
            question = Question(
                description= professional_question % (professional.description),
                answered=False
            )
            questions.append(question)
        background_investigation = BackgroundInvestigation(
            background_search_description= BUILT_IN_BACKGROUND_QUESTIONS_ZH_CN[ExperienceType.PROFESSIONAL] % (professional.description),
            searched=False
        )
        topic = Topic(
            questions=questions,
            experience=professional,
            background_investigation=background_investigation
        )
        questions = []
        res.append(topic)
    return res

def generate_report(topic_list: list[Topic]) -> str:
    res = []
    seen = set()

    for topic in topic_list:
        if topic.experience.experience_type == ExperienceType.ACADEMIC:
            if len(seen) == 0:
                    res.append("\n1.教育经历")
                    res.append("| 时间 | 院校 | 描述 | 是否是211 | 是否是985 | QS排名 |")
            
            if not topic.experience.description in seen:
                seen.add(topic.experience.description)
                line = "| %s - %s " % (topic.experience.begin_time, topic.experience.end_time)
                line += "| %s " % topic.experience.description
                line += "| %s " % topic.experience.supplement
                extra = []

                for question in topic.questions:
                    if question.report.answer.question_type == QuestionType.YESORNO or question.report.answer.question_type == QuestionType.NUMERIC:
                        if question.answered:
                            line += "| %s " % question.report.answer.answer
                        else:
                            line += "| 暂无 "
                    elif question.report.answer.question_type == QuestionType.DEFAULT:
                        extra.append(question.report.answer.answer)

                res.append(line)
                res.extend(extra)

    seen = set()
    for topic in topic_list:
        if topic.experience.experience_type == ExperienceType.PROFESSIONAL:
            if len(seen) == 0:
                    res.append("2.工作经历")
                    res.append("| 时间 | 公司 | 描述 |")
            
            if not topic.experience.description in seen:
                seen.add(topic.experience.description)
                line = "| %s - %s " % (topic.experience.begin_time, topic.experience.end_time)
                line += "| %s " % topic.experience.description
                line += "| %s " % topic.experience.supplement
                extra = []

                for question in topic.questions:
                    if question.report.answer.question_type == QuestionType.YESORNO or question.report.answer.question_type == QuestionType.NUMERIC:
                        if question.answered:
                            line += "| %s " % question.report.answer.answer
                        else:
                            line += "| 暂无 "
                    elif question.report.answer.question_type == QuestionType.DEFAULT:
                        extra.append(question.report.answer.answer)

                res.append(line)
                res.extend(extra)

    return "\n".join(res)