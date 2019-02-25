from flask import Flask, request, jsonify
from cerberus import Validator
from healthcheck import main as hc
from adjustment import main as adj
from flask_cors import CORS

APP = Flask(__name__)
CORS(APP)

@APP.route("/v1/healthcheck", methods=["POST"])
def healthcheck():
    """ Healthcheck API """
    schema = {
        "priority": {
            "type": "integer",
            "required": True
            },
        "annualInvestment": {
            "type": "float",
            "required": True
            },
        "initialInvestment": {
            "type": "float"
            },
        "goals": {
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "goalValue": {
                        "type": "float"
                        },
                    "goalID": {
                        "type": "float",
                        "required": True
                        },
                    "goalPriority": {
                        "type": "float",
                        "required": True
                        },
                    "goalDuration": {
                        "type": "float"
                        },
                    "frontendFee": {
                        "type": "float"
                        },
                    "backendFee": {
                        "type": "float"
                        },
                    "manageFee": {
                        "type": "float"
                        },
                    "discreteExpectedReturn": {
                        "type": "float"
                        },
                    "discreteStandardDeviation": {
                        "type": "float"
                        }
                    }
                }
            }
        }

    # ensure clean user input
    requester_input = request.json

    validator = Validator(schema)

    if not validator.validate(requester_input):
        return jsonify(validator.errors), 400

    # run healtcheck
    success, res = hc(requester_input)

    if success:
        return jsonify(res)

    return jsonify(res['error']), 400

@APP.route("/v1/adjustment", methods=["POST"])
def adjusment():
    """ Adjustment API """

    schema = {
        "priority": {
            "type": "integer",
            "required": True,
            "min": 1,
            "max": 6
            },
        "adjustment": {
            "type": "integer",
            "min": 1,
            "max": 6
            },
        "annualInvestment": {
            "type": "float",
            "required": True
            },
        "initialInvestment": {
            "type": "float"
            },
        "goals": {
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "backendFee": {
                        "type": "float"
                        },
                    "frontendFee": {
                        "type": "float"
                        },
                    "manageFee": {
                        "type": "float"
                        },
                    "goalValue": {
                        "type": "float"
                        },
                    "goalID": {
                        "required": True
                        },
                    "goalPriority": {
                        "required": True
                        },
                    "goalDuration": {
                        "type": "float"
                        },
                    "discreteExpectedReturn": {
                        "type": "float"
                        },
                    "discreteStandardDeviation": {
                        "type": "float"
                        },
                    "shortfall": {
                        "type": "float"
                        },
                    "surplus": {
                        "type": "float"
                        },
                    "probabilityScore": {
                        "type": "float"
                        },
                    "isAchieved": {
                        "type": "boolean"
                        },
                    "annualBreakdown": {
                        "type": "list",
                        "schema": {
                            "type": "dict",
                            "schema": {
                                "year": {
                                    "type": "float"
                                    },
                                "requiredInvestment": {
                                    "type": "float"
                                    },
                                "actualInvestment": {
                                    "type": "float"
                                    },
                                "shortfall": {
                                    "type": "float"
                                    },
                                "surplus": {
                                    "type": "float"
                                    },
                                "isAchieved": {
                                    "type": "boolean"
                                    },
                                "frontendFee": {
                                    "type": "float"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }


    # ensure clean user input
    requester_input = request.json

    validator = Validator(schema)

    if not validator.validate(requester_input):
        return jsonify(validator.errors), 400

    # run adjustment
    success, res = adj(requester_input)

    if success:
        return jsonify(res)

    return jsonify(res['error']), 400

@APP.route("/", methods=["GET"])
def health():
    return "healthy"

if __name__ == "__main__":
    APP.run(host="0.0.0.0", debug=True)
